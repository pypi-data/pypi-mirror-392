from .base import base


class User(base):
    def create(self, data):
        """
        创建用户
        https://tmc.qidian.qq.com/base/console/doc/13745?version=20250714

        创建单条客户数据
        {
            "identity":[ //客户身份
                {
                    "identityType":2, //客户身份类型
                    "identityValue":"18412301799" //客户身份值
                }
              ],
              "property":{ //客户属性
                  "name":"测试2222",
                  "arrayField": ["ab","cd"] //字符串数组类型示意
               }
        }
        """
        api_name = "cdp-entity/user/create"
        return self.request(
            api_name=api_name,
            json=data,
            method="POST",
        )

    def batch_create(self, data):
        """
        客户批量创建
        https://tmc.qidian.qq.com/base/console/doc/13746?version=20250714
        创建单条客户数据
        {
            "contents":[
                {
                    "identity":[
                        {
                            "identityType":2, //客户身份类型
                            "identityValue":"18412301799" //客户身份值
                            }
                    ],
                    "property":{ //客户属性
                        "属性字段Key":"属性值",
                        "arrayField": ["ab","cd"] //字符串数组类型示意
                    }
                }
            ]
        }
        """
        api_name = "cdp-entity/user/batchCreate"
        return self.request(
            api_name=api_name,
            json=data,
            method="POST",
        )

    def batch_edit(self, data):
        """
        客户批量更新
        https://tmc.qidian.qq.com/base/console/doc/13747?version=20250714

        请求示例：
        {
            "contents":[
                {
                    "id":"10283722" // 系统生成的统一客户OneID
                    "userIdentity": // 发布版本>=6.5
                        {
                            "identityType": 2,
                            "identityValue": "13428532631"
                        }
                    ,
                    "identity":[
                        {
                            "identityType":2,
                            "identityValue":"13601781755"
                        },
                        {
                            "identityType":1,
                            "identityValue":"18273631"
                        }
                    ],
                    "property":{
                        "客户属性字段Key":"客户属性值"
                        "arrayField": ["ab","cd"] //字符串数组类型示意
                    }
                }
            ]
        }
        """
        api_name = "cdp-entity/user/batchEdit"
        return self.request(
            api_name=api_name,
            json=data,
            method="POST",
        )

    def batch_delete(self, ids: list):
        """
        客户批量删除
        https://tmc.qidian.qq.com/base/console/doc/13748?version=20250714

        请求示例：
        {
            "ids":["66"] // 客户OneID列表
        }
        """
        api_name = "cdp-entity/user/batchDelete"
        return self.request(
            api_name=api_name,
            json={"ids": ids},
            method="POST",
        )

    def bind(self, contents: list):
        """
        客户身份绑定
        https://tmc.qidian.qq.com/base/console/doc/13749?version=20250714
        请求示例：
        {
            "contents": [
                {
                    "id": "10283722", // 系统生成的统一客户OneID
                    "identity":[ //客户身份
                        {
                            "identityType":2, //客户身份类型
                            "identityValue":"18412301799" //客户身份值
                        }
                    ]
                }
            ]
        }
        """
        api_name = "cdp-entity/user/identity/bind"
        return self.request(
            api_name=api_name,
            json={"contents": contents},
            method="POST",
        )

    def unbind(self, contents: list):
        """
        客户身份解绑
        https://tmc.qidian.qq.com/base/console/doc/14135?version=20250714
        请求示例：
        {
            "contents": [
                {
                    "id": "10283722", // 系统生成的统一客户OneID
                    "identity":[ //客户身份
                        {
                            "identityType":2, //客户身份类型
                            "identityValue":"18412301799" //客户身份值
                        }
                    ]
                }
            ]
        }
        """
        api_name = "cdp-entity/user/identity/unbind"
        return self.request(
            api_name=api_name,
            json={"contents": contents},
            method="POST",
        )

    def reset(self, contents: list):
        """
        客户身份重置
        https://tmc.qidian.qq.com/base/console/doc/14136?version=20250714
        请求示例：
        {
            "contents": [
                {
                    "id": "10283722", // 系统生成的统一客户OneID
                    "identity":[ //客户身份
                        {
                            "identityType":2, //客户身份类型
                            "identityValue":"18412301799" //客户身份值
                        }
                    ]
                }
            ]
        }
        """
        api_name = "cdp-entity/user/identity/reset"
        return self.request(
            api_name=api_name,
            json={"contents": contents},
            method="POST",
        )

    def queryList(self, pageNum: int = 1, pageSize: int = 10, queryCriteria: dict = {}):
        """
        客户列表查询
        https://tmc.qidian.qq.com/base/console/doc/13751?version=20250714
        请求示例：
        {
            "pageNum":1,
            "pageSize":10,
            "queryCriteria":{
                "filter": [
                    {
                        "property":"id",
                        "operation":"EQUAL",
                        "value":"67"
                    }
                ]
            }
        }
        查询条件没有filter时，表示查询所有客户； filter 之间默认是 and 关系；
        """
        api_name = "cdp-entity/user/queryList"
        queryCriteria = queryCriteria or {"filter": []}
        return self.request(
            api_name=api_name,
            json={
                "pageNum": pageNum,
                "pageSize": pageSize,
                "queryCriteria": queryCriteria,
            },
            method="POST",
        )

    def queryDetail(
        self, pageNum: int, pageSize: int, node: list = ["property"], items: list = []
    ):
        """
        客户详情查询
        基于不同类型的客户身份（客户OneID或其余客户身份，但只支持传某一种身份）查询客户详情（含客户属性、客户身份、客户标签），批量处理下单次上限100条。
        https://tmc.qidian.qq.com/base/console/doc/13752?version=20250714
        请求示例：
        {
            "pageNum":1,
            "pageSize":10,
            "node":["property"] //只返回property节点，指向返回节点
            "items":[
                {//只传saKey
                    "saKey" : "phone"
                    "saValue": "字段"
                },
                //只传oneId
                {
                    "oneId":"10283722" // 系统生成的统一客户OneID
                }
            ]
        }
        """
        api_name = "cdp-entity/user/queryDetail"
        return self.request(
            api_name=api_name,
            json={
                "pageNum": pageNum,
                "pageSize": pageSize,
                "node": node,
                "items": items,
            },
            method="POST",
        )

    def propertyList(self, pageNum: int, pageSize: int, queryCriteria: dict = {}):
        """
        客户元数据查询
        https://tmc.qidian.qq.com/base/console/doc/13761?version=20250714
        请求示例：
        {
        "pageNum": 1,
        "pageSize": 100,
        "queryCriteria": {
            "scene": "fieldManage",
            "withIdentityMeta": 1
        }
        }
        """
        api_name = "cdp-entity/user/property/list"
        return self.request(
            api_name=api_name,
            json={
                "pageNum": pageNum,
                "pageSize": pageSize,
                "queryCriteria": queryCriteria,
            },
            method="POST",
        )
