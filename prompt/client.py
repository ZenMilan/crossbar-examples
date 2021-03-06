from prompt_toolkit import prompt_async
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt

import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# http://python-prompt-toolkit.readthedocs.io/en/stable/pages/building_prompts.html#input-validation
class NumberValidator(Validator):

    def validate(self, document):
        text = document.text

        if text and not text.isdigit():
            i = 0

            # Get index of fist non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This input contains non-numeric characters',
                                  cursor_position=i)

class AsyncNumberValidator(Validator):

    def __init__(self, session):
        self._session = session
        Validator.__init__(self)

    async def validate(self, document):
        print('AsyncNumberValidator.validate')
        res = await self._session.call(u'com.example.validate_int', document.text)
        print(res)
        return res


class MyComponent(ApplicationSession):

    async def onJoin(self, details):
        print('Connected!')

        self._ticks = 0
        def onevent():
            self._ticks += 1
        await self.subscribe(onevent, u'com.example.tick')

        #validator = AsyncNumberValidator(self)
        validator = NumberValidator()
        print(validator)

        # we are waiting for user input now - but without blocking!
        # that is, eg the above event handler will continue to receive events while
        # the user is still not finished with input
        x = await prompt_async('x: ', validator=validator, patch_stdout=False)

        # user input is validated (in above, against a number validator) - but the value is
        # still returned as string, and hence needs to be converted
        x = int(x)
        y = self._ticks
        res = await self.call(u'com.example.add2', x, y)

        print("RPC succeded: {} + {} = {}".format(x, y, res))
        self.leave()

    def onDisconnect(self):
        loop = asyncio.get_event_loop()
        loop.stop()


if __name__ == '__main__':
    runner = ApplicationRunner(u"ws://localhost:8080/ws", u"realm1")
    runner.run(MyComponent)
