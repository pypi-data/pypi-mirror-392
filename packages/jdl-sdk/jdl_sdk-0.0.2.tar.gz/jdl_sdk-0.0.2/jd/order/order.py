#!/usr/bin/python3
# @Time    : 2025-10-21
# @Author  : Kevin Kong (kfx2007@163.com)

from jd.comm import Comm

class Order(Comm):
    """
    JD Order API
    """
    
    def precheck(
        self,
        sender_name: str = None,
        sender_mobile: str = None,
        sender_full_address: str = None,
        sender_warehouse_code: str = None,
        receiver_name: str = None,
        receiver_mobile: str = None,
        receiver_full_address: str = None,
        order_origin: int = 1,
        business_unit_code: str = None,
        cargoes: list = None,
        remark: str = None,
        products_req: dict = None,
        added_products: list = None,
        goods: list = None,
        pickup_start_time: int = None,
        pickup_end_time: int = None
    ):
        """
        预下单校验（参数全部展开）
        文档: https://api.jdl.com/ecap/v1/orders/precheck
        """
        url = "/ecap/v1/orders/precheck"
        request = {}
        # senderContact
        sender_contact = {}
        if sender_name:
            sender_contact["name"] = sender_name
        if sender_mobile:
            sender_contact["mobile"] = sender_mobile
        if sender_full_address:
            sender_contact["fullAddress"] = sender_full_address
        if sender_warehouse_code:
            sender_contact["warehouseCode"] = sender_warehouse_code
        if sender_contact:
            request["senderContact"] = sender_contact
        # receiverContact
        receiver_contact = {}
        if receiver_name:
            receiver_contact["name"] = receiver_name
        if receiver_mobile:
            receiver_contact["mobile"] = receiver_mobile
        if receiver_full_address:
            receiver_contact["fullAddress"] = receiver_full_address
        if receiver_contact:
            request["receiverContact"] = receiver_contact
        # 基础参数
        request["orderOrigin"] = order_origin
        request["customerCode"] = self.customer_code
        if business_unit_code:
            request["businessUnitCode"] = business_unit_code
        if cargoes:
            request["cargoes"] = cargoes
        if remark:
            request["remark"] = remark
        if products_req:
            request["productsReq"] = products_req
        if added_products:
            request["addedProducts"] = added_products
        if goods:
            request["goods"] = goods
        if pickup_start_time:
            request["pickupStartTime"] = pickup_start_time
        if pickup_end_time:
            request["pickupEndTime"] = pickup_end_time
        data = [request]
        return self.post(url, data)

    def create(
        self,
        # ---- 业务主键 ----
        order_id: str,
        # ---- 寄件人信息 senderContact ----
        sender_name: str,
        sender_full_address: str,
        sender_company: str = None,
        sender_mobile: str = None,
        sender_phone: str = None,
        sender_warehouse_code: str = None,
        sender_credentials_type: int = None,
        sender_credentials_number: str = None,
        sender_extend_props: dict = None,
        # ---- 收件人信息 receiverContact ----
        receiver_name: str = None,
        receiver_full_address: str = None,
        receiver_company: str = None,
        receiver_mobile: str = None,
        receiver_phone: str = None,
        receiver_warehouse_code: str = None,
        receiver_credentials_type: int = None,
        receiver_credentials_number: str = None,
        receiver_extend_props: dict = None,
        # ---- 订单来源及编码 ----
        order_origin: int = 1,
        customer_code: str = None,
        business_unit_code: str = None,
        # ---- 产品信息 productsReq 主产品 ----
        products_req: dict = None,
        # ---- 增值服务 addedProducts ----
        added_products: list = None,
        # ---- 结算方式 ----
        settle_type: int = 3,
        c2b_added_settle_type_info: dict = None,
        # ---- 货品信息 cargoes (仅支持一个对象) ----
        cargo: dict = None,
        # ---- 商品信息 goods （C2B退货场景）----
        goods: list = None,
        goods_add_products: list = None,
        serial_nos: list = None,
        # ---- 揽收/配送时间 ----
        pickup_start_time: int = None,
        pickup_end_time: int = None,
        expect_delivery_start_time: int = None,
        expect_delivery_end_time: int = None,
        pickup_type: int = 1,
        delivery_type: int = 1,
        # ---- 备注 ----
        remark: str = None,
        # ---- 渠道信息 channelInfo ----
        channel_code: str = None,
        channel_order_code: str = None,
        second_level_channel: str = None,
        second_level_channel_order_no: str = None,
        waybill_code: str = None,
        channel_extend_props: dict = None,
        # ---- 配送场景 ----
        sub_order_origin: int = None,
        # ---- 报关 customsInfo ----
        customs_info: dict = None,
        attachment_infos: list = None,
        # ---- 其他 ----
        extend_props: dict = None,
    ):
        """
        创建京东快递订单
        接口: https://api.jdl.com/ecap/v1/orders/create

        参数说明(与官方字段映射):
        order_id -> orderId (商家订单号, 1-50唯一)
        sender_* -> senderContact.* (寄件人信息, name/fullAddress 必填, mobile 或 phone 至少一个)
        receiver_* -> receiverContact.* (收件人信息, name/fullAddress 建议必填, mobile 或 phone 至少一个)
        order_origin -> orderOrigin (0-c2c 1-b2c 2-c2b 4-kyb2c 5-kyc2c)
        customer_code -> customerCode (orderOrigin 为1或2时必填; 若不传使用 self.customer_code)
        business_unit_code -> businessUnitCode (orderOrigin=4时必填, 5不传)
        products_req -> productsReq 主产品: {"productCode": "ed-m-0001", "productAttrs": {...}, "extendProps": {...}}
        added_products -> addedProducts 增值产品列表: [{"productCode": "ed-a-0002", ...}]
        settle_type -> settleType (付款方式: 1寄付 2到付 3月结 5多方收费)
        c2b_added_settle_type_info -> c2bAddedSettleTypeInfo 多方收费子结构
        cargo -> cargoes[0] 货品信息 CommonCargoInfo (name, quantity, weight, volume, length, width, hight, remark, cargoCode, goods, serialNos...)
        goods -> goods 商品列表 (退货/C2B场景)
        goods_add_products -> goodsAddProducts 商品维度服务列表
        serial_nos -> cargo.serialNos 序列号列表: [{"serialCode": "xxx"}, ...]
        pickup_start_time -> pickupStartTime (毫秒级时间戳)
        pickup_end_time -> pickupEndTime
        expect_delivery_start_time -> expectDeliveryStartTime
        expect_delivery_end_time -> expectDeliveryEndTime
        pickup_type -> pickupType (1上门 2自送)
        delivery_type -> deliveryType (1送货上门 2自提)
        remark -> remark (面单备注, 显示截取前50字)
        渠道信息 channel_* -> commonChannelInfo.*
        waybill_code -> waybillCode (预制条码/带单号)
        channel_extend_props -> commonChannelInfo.extendProps
        sub_order_origin -> subOrderOrigin (配送场景 0纯配 1仓配 3零包裹方案)
        customs_info -> customsInfo (跨境报关信息结构)
        attachment_infos -> customsInfo.attachmentInfos 附件列表
        extend_props -> extendProps (订单级扩展字段)

        返回: API 响应 JSON

        注意: 本方法不做严格必填校验, 需调用方按业务规则保证必填字段.
        """
        url = "/ecap/v1/orders/create"
        request = {"orderId": order_id}

        # ----- senderContact -----
        sender_contact = {"name": sender_name, "fullAddress": sender_full_address}
        if sender_company:
            sender_contact["company"] = sender_company
        if sender_mobile:
            sender_contact["mobile"] = sender_mobile
        if sender_phone:
            sender_contact["phone"] = sender_phone
        if sender_warehouse_code:
            sender_contact["warehouseCode"] = sender_warehouse_code
        if sender_credentials_type is not None:
            sender_contact["credentialsType"] = sender_credentials_type
        if sender_credentials_number:
            sender_contact["credentialsNumber"] = sender_credentials_number
        if sender_extend_props:
            sender_contact["extendProps"] = sender_extend_props
        request["senderContact"] = sender_contact

        # ----- receiverContact -----
        if receiver_name or receiver_full_address:
            receiver_contact = {}
            if receiver_name:
                receiver_contact["name"] = receiver_name
            if receiver_full_address:
                receiver_contact["fullAddress"] = receiver_full_address
            if receiver_company:
                receiver_contact["company"] = receiver_company
            if receiver_mobile:
                receiver_contact["mobile"] = receiver_mobile
            if receiver_phone:
                receiver_contact["phone"] = receiver_phone
            if receiver_warehouse_code:
                receiver_contact["warehouseCode"] = receiver_warehouse_code
            if receiver_credentials_type is not None:
                receiver_contact["credentialsType"] = receiver_credentials_type
            if receiver_credentials_number:
                receiver_contact["credentialsNumber"] = receiver_credentials_number
            if receiver_extend_props:
                receiver_contact["extendProps"] = receiver_extend_props
            request["receiverContact"] = receiver_contact

        # ----- 基础枚举/来源 -----
        request["orderOrigin"] = order_origin
        if customer_code:
            request["customerCode"] = customer_code
        else:
            # fallback to instance customer_code if present
            if getattr(self, "customer_code", None):
                request["customerCode"] = self.customer_code
        if business_unit_code:
            request["businessUnitCode"] = business_unit_code

        # ----- 产品信息 -----
        if products_req:
            request["productsReq"] = products_req
        if added_products:
            request["addedProducts"] = added_products

        # ----- 结算方式 -----
        if settle_type is not None:
            request["settleType"] = settle_type
        if c2b_added_settle_type_info:
            request["c2bAddedSettleTypeInfo"] = c2b_added_settle_type_info

        # ----- 货品信息 cargoes -----
        if cargo:
            cargo_obj = dict(cargo)  # copy
            if serial_nos:
                cargo_obj["serialNos"] = serial_nos
            request["cargoes"] = [cargo_obj]

        # ----- 商品信息 goods (退货场景) -----
        if goods:
            request["goods"] = goods
        if goods_add_products:
            request["goodsAddProducts"] = goods_add_products

        # ----- 时间相关 -----
        if pickup_start_time:
            request["pickupStartTime"] = pickup_start_time
        if pickup_end_time:
            request["pickupEndTime"] = pickup_end_time
        if expect_delivery_start_time:
            request["expectDeliveryStartTime"] = expect_delivery_start_time
        if expect_delivery_end_time:
            request["expectDeliveryEndTime"] = expect_delivery_end_time
        if pickup_type is not None:
            request["pickupType"] = pickup_type
        if delivery_type is not None:
            request["deliveryType"] = delivery_type

        # ----- 备注 -----
        if remark:
            request["remark"] = remark

        # ----- 渠道信息 -----
        channel_info = {}
        if channel_code:
            channel_info["channelCode"] = channel_code
        if channel_order_code:
            channel_info["channelOrderCode"] = channel_order_code
        if second_level_channel:
            channel_info["secondLevelChannel"] = second_level_channel
        if second_level_channel_order_no:
            channel_info["secondLevelChannelOrderNo"] = second_level_channel_order_no
        if channel_extend_props:
            channel_info["extendProps"] = channel_extend_props
        if channel_info:
            request["commonChannelInfo"] = channel_info
        if waybill_code:
            request["waybillCode"] = waybill_code

        # ----- 配送场景 -----
        if sub_order_origin is not None:
            request["subOrderOrigin"] = sub_order_origin

        # ----- 报关信息 -----
        if customs_info:
            customs = dict(customs_info)
            if attachment_infos:
                customs["attachmentInfos"] = attachment_infos
            request["customsInfo"] = customs
        elif attachment_infos:
            # 如果只给附件也需要 customsInfo 结构
            request["customsInfo"] = {"attachmentInfos": attachment_infos}

        # ----- 订单扩展字段 -----
        if extend_props:
            request["extendProps"] = extend_props

        # API 期望数组批量，这里按单条封装
        data = [request]
        return self.post(url, data)
    
    def cancel(
        self,
        waybill_code: str = None,
        order_code: str = None,
        customer_order_id: str = None,
        order_origin: int = 1,
        customer_code: str = None,
        business_unit_code: str = None,
        cancel_reason: str = None,
        cancel_reason_code: int = 1,
        cancel_type: int = None,
        subscribe_intercept: str = None,
    ):
        """
        取消京东快递订单
        接口: https://api.jdl.com/ecap/v1/orders/cancel

        与官方字段映射:
        waybill_code -> waybillCode 京东物流运单号 (运单号/京东订单号/商家订单号 三者至少其一)
        order_code -> orderCode 京东物流订单号 (同上三选一)
        customer_order_id -> customerOrderId 商家订单号 (同上三选一)
        order_origin -> orderOrigin 下单来源 0-c2c 1-b2c 2-c2b 4-kyb2c 5-kyc2c (与原下单保持一致; 需求明确只列到2这里保留1/2常用) 
        customer_code -> customerCode orderOrigin=1 时必填 (若不传尝试使用 self.customer_code)
        business_unit_code -> businessUnitCode orderOrigin=4 时必填, 5 不传
        cancel_reason -> cancelReason 取消原因 文本 1-30 长度
        cancel_reason_code -> cancelReasonCode 枚举: 1-用户发起取消 2-超时未支付
        cancel_type -> cancelType 枚举: orderOrigin=0 -> 0; orderOrigin=1或2 -> 1
        subscribe_intercept -> subscribeIntercept 自动订阅拦截信息 "1" 表示订阅

        返回: API 响应 JSON

        业务校验(本方法内部简要处理):
        - waybill_code/order_code/customer_order_id 至少传一个, 否则抛 ValueError
        - cancel_reason 必填
        - cancel_type 若未显式传入, 按 order_origin 自动推导
        """
        url = "/ecap/v1/orders/cancel"
        # 基本必填校验
        if not (waybill_code or order_code or customer_order_id):
            raise ValueError("必须至少提供 waybill_code/order_code/customer_order_id 之一用于定位订单")
        if not cancel_reason:
            raise ValueError("cancel_reason 取消原因必填")

        request = {"orderOrigin": order_origin, "cancelReason": cancel_reason, "cancelReasonCode": cancel_reason_code}
        if waybill_code:
            request["waybillCode"] = waybill_code
        if order_code:
            request["orderCode"] = order_code
        if customer_order_id:
            request["customerOrderId"] = customer_order_id

        # customerCode 优先显式参数, 否则尝试实例属性
        if customer_code:
            request["customerCode"] = customer_code
        elif order_origin == 1 and getattr(self, "customer_code", None):
            request["customerCode"] = self.customer_code

        if business_unit_code:
            request["businessUnitCode"] = business_unit_code

        # 推导 cancelType
        if cancel_type is None:
            if order_origin == 0:
                cancel_type = 0
            elif order_origin in (1, 2):
                cancel_type = 1
        if cancel_type is not None:
            request["cancelType"] = cancel_type

        if subscribe_intercept:
            request["subscribeIntercept"] = subscribe_intercept

        data = [request]
        return self.post(url, data)
    
    def print(
        self,
        # --- 顶层字段 ---
        template_code: str,
        operator: str,
        task_id: str,
        output_config: list,
        # --- 简化单条打印数据直传(与 print_data 二选一) ---
        order_number: str = None,
        carrier_code: str = None,
        bill_code_value: str = None,
        bill_code_type: str = None,
        scene: int = None,
        customized_print_data: dict = None,
        package_begin_index: int = None,
        package_end_index: int = None,
        # customerPrintData 内部字段(若提供任一则组装) ---
        transport_type: int = None,
        product_code: str = None,
        added_service_codes: list = None,
        remark: str = None,
        business_order_id: str = None,
        sender_name: str = None,
        sender_mobile: str = None,
        sender_address: str = None,
        receiver_name: str = None,
        receiver_mobile: str = None,
        receiver_address: str = None,
        package_name: str = None,
        warehouse_code: str = None,
        weight: float = None,
        package_count: int = None,
        fresh_type: str = None,
        settle_type: int = None,
        # --- 直接传完整打印数据列表 ---
        print_data: list = None,
    ):
        """
        电子面单渲染打印
        接口: https://api.jdl.com/cloud/print/render

        顶层字段 (queryRenderDTO 内):
        customer_code -> customerCode (商家结算编码 / 业主号 / 事业部编码)
        template_code -> templateCode (模板编码 标准或自定义区模板)
        operator -> operator (操作打单人账号)
        task_id -> taskId (调用方唯一任务号)
        output_config -> outputConfig 列表: 每项 OutputConfigDTO {outputType, dataFormat, fileFormat}

        打印数据 printData (列表). 可通过:
        1) 直接传入 print_data 列表 (优先)
        2) 使用简化单条参数 (order_number 等) 自动组装一条 PrintDataDTO

        PrintDataDTO 字段映射:
        order_number -> orderNumber (业务单号)
        carrier_code -> carrierCode (承运商编码: JD 等)
        bill_code_value -> billCodeValue (单据号: 运单/包裹/箱号)
        bill_code_type -> billCodeType (waybillCode | packageCode | boxCode)
        scene -> scene (4快递/5快运/6大件)
        customized_print_data -> customizedPrintData (自定义区数据)
        package_begin_index -> packageBeginIndex (快运一单多件起始包裹号, 仅 scene=5 且 billCodeType=waybillCode 生效)
        package_end_index -> packageEndIndex (快运一单多件结束包裹号)

        customerPrintData 组合字段: 当相关任一值提供则组装
        transport_type -> transportType (1航空/2陆运/4高铁)
        product_code -> productCode (主产品编码 ed-m-0001 等)
        added_service_codes -> addedServiceCode (增值服务编码列表)
        remark -> remark (备注)
        business_order_id -> businessOrderId (客户订单号)
        sender_* / receiver_* 地址与姓名手机号
        package_name -> packageName
        warehouse_code -> warehouseCode
        weight -> weight (kg 两位小数)
        package_count -> packageCount (包裹数)
        fresh_type -> freshType (cold/freezing/deepCool)
        settle_type -> settleType (0寄付月结 1到付现结 2寄付现结)

        返回: API 响应 JSON

        校验:
        - output_config 必填非空
        - template_code/customer_code/operator/task_id 必填
        - print_data 与 简化单条参数不可同时为空
        - 若使用简化单条且需要标准数据, carrier_code/scene/bill_code_type/bill_code_value 应配合提供

        注意: 方法名 print 会遮蔽内置 print 函数的实例属性访问, 调用时请使用 order_api.print(...)
        """
        url = "/cloud/print/render"

        customer_code = self.customer_code
        if not template_code:
            raise ValueError("template_code 必填")
        if not operator:
            raise ValueError("operator 必填")
        if not task_id:
            raise ValueError("task_id 必填")
        if not output_config or not isinstance(output_config, list):
            raise ValueError("output_config 必须为非空列表")

        query = {
            "customerCode": customer_code,
            "templateCode": template_code,
            "operator": operator,
            "taskId": task_id,
            "outputConfig": output_config,
        }

        # 组装 printData
        if print_data:
            query["printData"] = print_data
        else:
            if not order_number:
                raise ValueError("未提供 print_data 列表时必须至少提供 order_number 用于组装单条 PrintDataDTO")
            pd = {"orderNumber": order_number}
            # 标准数据字段 (联合必填策略由外部保证; 这里仅条件添加)
            if carrier_code:
                pd["carrierCode"] = carrier_code
            if bill_code_value:
                pd["billCodeValue"] = bill_code_value
            if bill_code_type:
                pd["billCodeType"] = bill_code_type
            if scene is not None:
                pd["scene"] = scene
            if customized_print_data:
                pd["customizedPrintData"] = customized_print_data
            if package_begin_index is not None:
                pd["packageBeginIndex"] = package_begin_index
            if package_end_index is not None:
                pd["packageEndIndex"] = package_end_index

            # customerPrintData 组合
            customer_print = {}
            if transport_type is not None:
                customer_print["transportType"] = transport_type
            if product_code:
                customer_print["productCode"] = product_code
            if added_service_codes:
                customer_print["addedServiceCode"] = added_service_codes
            if remark:
                customer_print["remark"] = remark
            if business_order_id:
                customer_print["businessOrderId"] = business_order_id
            if sender_name:
                customer_print["senderName"] = sender_name
            if sender_mobile:
                customer_print["senderMobile"] = sender_mobile
            if sender_address:
                customer_print["senderAddress"] = sender_address
            if receiver_name:
                customer_print["receiverName"] = receiver_name
            if receiver_mobile:
                customer_print["receiverMobile"] = receiver_mobile
            if receiver_address:
                customer_print["receiverAddress"] = receiver_address
            if package_name:
                customer_print["packageName"] = package_name
            if warehouse_code:
                customer_print["warehouseCode"] = warehouse_code
            if weight is not None:
                customer_print["weight"] = weight
            if package_count is not None:
                customer_print["packageCount"] = package_count
            if fresh_type:
                customer_print["freshType"] = fresh_type
            if settle_type is not None:
                customer_print["settleType"] = settle_type
            if customer_print:
                pd["customerPrintData"] = customer_print

            query["printData"] = [pd]
            

        data = [query]
        return self.post(url, data, lopdn='jdcloudprint')

    def rate(
        self,
        waybill_code,
        order_code,
        order_origin,
        customer_code,
        business_unit_code
    ):
        """
        查询订单/运单的实际费用（运费）。

        Endpoint:
            /ecap/v1/orders/actualfee/query

        参数说明 (字段名按 JD 文档):
          waybillCode (str, optional) 运单号
          orderCode (str, optional) 订单号
          orderOrigin (str, optional) 订单来源
          customerCode (str, optional) 客户编码；未传则尝试用实例 customer_code
          businessUnitCode (str, optional) BU 编码

        必填逻辑:
          waybillCode 与 orderCode 至少一个必填，否则抛错。

        Returns:
          dict: 解析后的响应 JSON
        """
        if not (waybill_code or order_code):
            raise ValueError("waybillCode 与 orderCode 至少需要提供一个")

        payload = {}
        if waybill_code:
            payload["waybillCode"] = waybill_code
        if order_code:
            payload["orderCode"] = order_code
        if order_origin:
            payload["orderOrigin"] = order_origin
        if customer_code or self.customer_code:
            payload["customerCode"] = customer_code or self.customer_code
        if business_unit_code:
            payload["businessUnitCode"] = business_unit_code

        # 直接复用签名逻辑（建议把 post() 里硬编码去掉）
        return self.post(
            "/ecap/v1/orders/actualfee/query",
            data=[payload],
        )


