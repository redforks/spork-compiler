import spork.test

class MyTestCase(spork.test.TestBase):
    def assertEqual(self, x, y):
        if type(x) == str == type(y):
            if '\n' not in x:
                x = x.replace(';', ';\n')
            if '\n' not in y:
                y = y.replace(';', ';\n')
            return self.assertMultiLineEqual(x, y)
        else:
            super(MyTestCase, self).assertEqual(x, y)

