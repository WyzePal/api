# See readme.md for instructions on running this code.
from typing import Any, Dict

class HelpHandler(object):
    def usage(self) -> str:
        return '''
            This plugin will give info about WyzePal to
            any user that types a message saying "help".

            This is example code; ideally, you would flesh
            this out for more useful help pertaining to
            your WyzePal instance.
            '''

    def handle_message(self, message: Dict[str, str], bot_handler: Any) -> None:
        help_content = "Info on WyzePal can be found here:\nhttps://github.com/wyzepal/wyzepal"
        bot_handler.send_reply(message, help_content)

handler_class = HelpHandler
