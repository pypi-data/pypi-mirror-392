from .base import base


class OPen(base):
    def batch_create(self, entityKey, contents):
        """
        实体批量创建
        https://tmc.qidian.qq.com/base/console/doc/13764?version=20250714
        {
        "entityName": "",
        "entityKey": "",
        "contents": [
            {
            "property": {
                // 实体主键
                "keyId" : "对应客户侧唯一ID" // 必填，实体数据主键ID，由一方上传
                "实体字段KEY": "实体字段值",
                "arrayField": ["ab","cd"] //字符串数组类型示意

            },
            "identity": [{
                "identityKey" : "",
                "identityValue"
            }]
        ],
        "mergeRule": 0
        }
        """
        api_name = "cdp-entity/open/dataBatchAdd"
        return self.request(
            api_name=api_name,
            json={"entityKey": entityKey, "contents": contents, "mergeRule": 0},
            method="POST",
        )

    def edit(self, entityKey: str, keyId: str, property: dict, identity: list = []):
        """
        实体更新
        https://tmc.qidian.qq.com/base/console/doc/13765?version=20250714
        {
        "entityKey": "",
        "keyId": "", // 必填，实体数据主键ID
        "property": {
            "实体字段KEY": "实体字段值" //自定义字段和系统字段
            "arrayField": ["ab","cd"] //字符串数组类型示意
        },
        "identity": [{
                "identityKey" : "",
                "identityValue"
            }]
        }
        """
        api_name = "cdp-entity/open/dataEdit"
        data = {
            "entityKey": entityKey,
            "keyId": keyId,
            "property": property,
            "identity": identity,
        }
        return self.request(
            api_name=api_name,
            json=data,
            method="POST",
        )

    def batch_delete(self, entityKey: str, keyIdList: list):
        """
        实体批量删除
        https://tmc.qidian.qq.com/base/console/doc/13766?version=20250714

        请求示例：
        {
        "entityKey": "",
        "keyIdList": [
            ""
        ]
        }
        """
        api_name = "cdp-entity/open/batchDelete"
        return self.request(
            api_name=api_name,
            json={"entityKey": entityKey, "keyIdList": keyIdList},
            method="POST",
        )

    def dataList(self, pageNum: int = 1, pageSize: int = 10, queryCriteria: dict = {}):
        """
        实体列表查询
        https://tmc.qidian.qq.com/base/console/doc/13768?version=20250714
        请求示例：
        {
        "pageNum": 0,
        "pageSize": 0,
        "queryCriteria": {
            "entityKey": "",
            "keyIdList": [
            ""
            ],
            "idList": [
            ""
            ],
            "property": [
            "字段Key1","字段Key2", //只返回key1 和key2
            ],
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
        api_name = "cdp-entity/open/dataList"
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

    def dataDetail(
        self,
        pageNum: int,
        pageSize: int,
        entityKey: str,
        keyIdList: list = [],
        property: list = [],
    ):
        """
        实体详情查询
        基于不同类型的客户身份（客户OneID或其余客户身份，但只支持传某一种身份）查询客户详情（含客户属性、客户身份、客户标签），批量处理下单次上限100条。
        https://tmc.qidian.qq.com/base/console/doc/13769?version=20250714
        请求示例：
        {
        "entityKey": "",
        "keyIdList": [
            ""
        ],
        "property": [
            "字段Key1","字段Key2", //只返回key1 和key2
        ]
        }
        """
        api_name = "cdp-entity/open/dataDetail"
        return self.request(
            api_name=api_name,
            json={
                "pageNum": pageNum,
                "pageSize": pageSize,
                "entityKey": entityKey,
                "keyIdList": keyIdList,
                "property": property,
            },
            method="POST",
        )
