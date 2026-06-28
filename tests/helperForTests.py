from unittest import TestCase

class baseTestSuite(TestCase):
    def exceptionMessageTester(self, ex, exMsgToCheck, assertMsg, func, *funcArgs, **funcKwargs):
        with self.assertRaises(ex) as error:
            func(*funcArgs, **funcKwargs)
        exceptionmessage = str(error.exception)
        self.assertTrue(exceptionmessage.lower().startswith(exMsgToCheck.lower()),
                        msg=f"{assertMsg} {exceptionmessage}")