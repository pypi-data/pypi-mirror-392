#!/usr/bin/python3
# @Time    : 2025-10-18
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from unittest.mock import patch, MagicMock
from jd.api import JDL

ORDER_ID = "TESTORDER001"

class TestComm(unittest.TestCase):
    
    def setUp(self):
        self.jd = JDL(
            "588bd6c100af4c36b9521bf0068cebf9",
            "3a39e9e08a4e42d1aaa1fec5f9f9cf98",
            "010K9619222",
            "70c225e73c3d4862957e8960a3548152",
            sandbox=False,
        )
        
    # def test_precheck(self):
    #     sender_full_address = "香港特别行政区九龙城区"
    #     receiver_full_address = "香港特别行政区九龙城区"
    #     response = self.jd.order.precheck(
    #         "张三","18511112222",
    #         sender_full_address,
    #         receiver_name="李四", receiver_mobile="13900001111",
    #         receiver_full_address=receiver_full_address,
    #     )
    #     # print(response)
    #     self.assertEqual(response.get("success"), True, msg=response)
        
    # def test_create_order(self):
    #     response = self.jd.order.create(
    #         order_id=ORDER_ID,
    #         sender_name="张三",
    #         sender_full_address="北京市朝阳区望京街道100号",
    #         receiver_name="李四",
    #         receiver_full_address="上海市浦东新区世纪大道200号",
    #         cargo={
    #             "name": "电子产品",
    #             "quantity": 1,
    #             "weight": 2.5,
    #             "volume": 0.01,
    #             "remark": "测试订单",
    #         },
    #         sender_mobile="13800000000",
    #         receiver_mobile="13900000000",
    #         products_req={
    #             "productCode": "ed-m-0001",
    #         }
    #     )
    #     self.assertEqual(response.get("success"), True, msg=response)

    # def test_cancel_order(self):
    #     # 依赖已创建的订单，使用商家订单号取消
    #     response = self.jd.order.cancel(
    #         customer_order_id=ORDER_ID,
    #         order_origin=1,
    #         cancel_reason="用户发起取消",
    #         cancel_reason_code=1,
    #         subscribe_intercept="1",
    #     )
    #     self.assertEqual(response.get("success"), True, msg=response)
    
    def test_print(self):
        """测试电子面单渲染接口 cloud/print/render"""
        response = self.jd.order.print(
            template_code="jdkd76x130",   # 假设有效模板编码
            operator="tester-001",
            task_id="task-print-001",
            output_config=[{"outputType": "1", "dataFormat": "1", "fileFormat": "1"}],
            order_number="23847621836421",
            carrier_code="JD",
            bill_code_value="JDV023721566237",
            bill_code_type="waybillCode",
            scene="4",
            sender_name="张三",
            sender_address="北京市海淀区西二旗",  # 必填地址场景
            receiver_name="李四",
            receiver_address="上海市浦东新区陆家嘴",
            # weight=1.2,
            product_code="ed-m-0001",
        )
        print(response)
        self.assertEqual(response.get("success"), True, msg=response)
    
    # def test_rate(self):
    #     """测试运费试算接口 order/rate"""
    #     response = self.jd.order.rate(
    #         waybill_code="JDX010033826856",
    #         order_code=ORDER_ID,
    #     )
    #     # print(response)
    #     self.assertIn("freight", response, msg=response)
    
        
if __name__ == "__main__":
    unittest.main()