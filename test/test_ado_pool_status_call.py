#!/usr/bin/env python3

import unittest
import ado_pool_status_call

class AgentStatusOutputTest(unittest.TestCase):
    
    def test_statusoutput(self):
        poolinput = '11'
        result = ado_pool_status_call.ado_call(poolinput)
        self.assertIn(result, 'count') 

# if __name__ == '__main__':
#     unittest.main()