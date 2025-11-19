import os
import logging
import re
import html
import requests
from typing import List, Dict, Any, Optional, Union


class TelegramNotifier:
    """
    A Telegram analog of your SlackNotifier.
    Provides message sending, file uploading, HTML-safe formatting,
    multi-target support, and structured logging.
    """

    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str, timeout: int = 30, log: bool = True):
        if not token:
            raise ValueError("Telegram bot token cannot be empty.")

        self.token = token
        self.timeout = timeout

        self.logger = logging.getLogger(f"easy_cherry.telegram.{id(self)}")
        self.logger.propagate = False

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        if log:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.addHandler(logging.NullHandler())

        # Test authentication
        resp = self._api_call("getMe")
        if not resp.get("ok"):
            raise ConnectionError(f"Telegram auth failed: {resp.get('description', resp)}")

        bot_info = resp["result"]
        self.bot_id = bot_info["id"]
        self.bot_name = bot_info["username"]

        self.logger.info(
            f"Authenticated as @{self.bot_name} (ID: {self.bot_id}). Timeout: {timeout}s"
        )

    # --------------------------------------------------------------------------
    # Internal API Helper
    # --------------------------------------------------------------------------

    def _api_call(self, method: str, params=None, files=None) -> Dict[str, Any]:
        """Makes a direct request to the Telegram Bot API."""
        url = self.TELEGRAM_API_URL.format(token=self.token, method=method)
        try:
            if files:
                resp = requests.post(url, data=params, files=files, timeout=self.timeout)
            else:
                resp = requests.post(url, json=params, timeout=self.timeout)
            
            resp.raise_for_status() # Raise an exception for bad status codes
            return resp.json()
        
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error calling Telegram API ({method}): {e}")
            # Try to return JSON error response if possible
            try:
                return e.response.json()
            except Exception:
                return {"ok": False, "error": str(e)}
        except Exception as e:
            self.logger.error(f"Error calling Telegram API ({method}): {e}")
            return {"ok": False, "error": str(e)}

    # --------------------------------------------------------------------------
    # New Method: Get Updates
    # --------------------------------------------------------------------------
    def get_updates(self, offset: int = 0, timeout: int = 30) -> Dict[str, Any]:
        """Polls the Telegram API for new messages."""
        self.logger.debug(f"Polling for updates with offset {offset}...")
        return self._api_call(
            "getUpdates",
            {"offset": offset, "timeout": timeout}
        )

    # --------------------------------------------------------------------------
    # Utility
    # --------------------------------------------------------------------------

    def _process_message(self, message: str) -> str:
        """
        Processes the message before sending.
        Since we use parse_mode="HTML", we trust the message
        is already formatted correctly.
        """
        # --- FIX ---
        # The original logic was escaping the HTML (html.escape),
        # which prevented Telegram from parsing it.
        # This version now passes the HTML through directly.
        
        html_pattern = re.compile(r"<([a-z][a-z0-9]*)\b[^>]*>", re.IGNORECASE)

        if html_pattern.search(message):
            self.logger.info("HTML detected. Passing through for Telegram to parse.")

        return message

    # --------------------------------------------------------------------------
    # Target resolution
    # --------------------------------------------------------------------------

    def _resolve_target(self, target: str) -> str:
        """
        Telegram targets are:
            - numeric chat IDs
            - @usernames
            - @channel or @group usernames
        No API exists to resolve username → ID unless user has chatted with bot.
        """
        # This method is fine as-is. Telegram API accepts @usernames directly.
        return target

    # --------------------------------------------------------------------------
    # Main Message Sender
    # --------------------------------------------------------------------------

    def send(
        self,
        targets: Union[str, List[str]],
        message: str,
        file_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:

        if isinstance(targets, str):
            targets = [targets]

        # --- FIX ---
        # The _process_message method is now corrected, so this `processed`
        # string will contain the raw HTML (e.g., "<b>Hello</b>")
        processed = self._process_message(message)
        responses = {}

        for target in targets:
            chat_id = self._resolve_target(target)

            if not file_paths:
                self.logger.info(f"Sending message to {target}...")
                resp = self._api_call(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": processed,
                        "parse_mode": "HTML",
                    }
                )
                responses[target] = resp
                continue

            # File sending
            file_results = []
            for path in file_paths:
                if not os.path.exists(path):
                    self.logger.error(f"File not found: {path}")
                    file_results.append({"ok": False, "error": "file_not_found", "path": path})
                    continue

                self.logger.info(f"Uploading file to {target}: {path}")

                try:
                    with open(path, "rb") as f:
                        resp = self._api_call(
                            "sendDocument",
                            {"chat_id": chat_id, "caption": processed, "parse_mode": "HTML"},
                            files={"document": f},
                        )
                    file_results.append(resp)
                except Exception as e:
                    self.logger.error(f"Failed to upload file {path}: {e}")
                    file_results.append({"ok": False, "error": str(e), "path": path})

            responses[target] = {"ok": True, "files": file_results}

        return responses

    # --------------------------------------------------------------------------
    # Block-like Message Support (emulated using formatted text)
    # --------------------------------------------------------------------------

    def send_blocks(
        self,
        targets: Union[str, List[str]],
        blocks: List[Dict[str, Any]],
        fallback_text: str = ""
    ) -> Dict[str, Any]:
        """
        Telegram does not support blocks.
        We convert them into formatted HTML text.
        """
        html_msg = ""

        for block in blocks:
            bt = block.get("type")
            if bt == "header":
                # The text content from create_header_block is now safely escaped
                text = block["text"]["text"]
                html_msg += f"<b><u>{text}</u></b>\n\n"

            elif bt == "section" and "fields" in block:
                for field in block["fields"]:
                    # --- FIX ---
                    # Do not escape field['text'] here.
                    # It is already formatted as HTML by create_fields_section.
                    html_msg += f"{field['text']}\n"
                html_msg += "\n"

            else:
                # Fallback for unknown blocks, escape this to be safe
                html_msg += f"{html.escape(str(block))}\n\n"

        return self.send(targets, html_msg or fallback_text)

    # --------------------------------------------------------------------------
    # Helpers similar to Slack version
    # --------------------------------------------------------------------------

    @staticmethod
    def create_header_block(title: str) -> Dict[str, Any]:
        # --- FIX ---
        # Escape the user-provided title to prevent HTML injection.
        # The `send_blocks` method will wrap this in <b><u> tags.
        return {
            "type": "header",
            "text": {"type": "plain_text", "text": html.escape(title)}
        }

    @staticmethod
    def create_fields_section(fields: Dict[str, str]) -> Dict[str, Any]:
        # --- FIX ---
        # Escape the user-provided keys (k) and values (v)
        # to prevent HTML injection.
        items = [f"<b>{html.escape(k)}:</b> {html.escape(v)}" for k, v in fields.items()]
        return {
            "type": "section",
            "fields": [{"text": t} for t in items]
        }