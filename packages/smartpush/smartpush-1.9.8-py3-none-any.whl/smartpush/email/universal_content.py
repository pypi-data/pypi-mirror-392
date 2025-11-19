import json
import time
from smartpush.base.request_base import RequestBase
from smartpush.base.url_enum import *
from smartpush.email.schema import *
from smartpush.utils import ListDictUtils


def gen_universal_request_param(universalId, schema, **kwargs):
    """

    :param schema:
    :type universalId:
    kwargs :
    universalName/subUniversal_id/type/flowModal
    """
    universalName = kwargs.get('universalName', gen_universal_name(schema))
    result_schema = get_universal_schema(schema=schema, _id=generate_UUID(9), universalId=universalId,
                                         universalName=universalName)
    requestParam = {
        "universalId": universalId,
        "universalName": universalName,
        "schema": json.dumps(result_schema),
        "subUniversalId": kwargs.get('subUniversal_id', universalId),
        "type": kwargs.get('type', 0),
        "blockType": result_schema.get('type'),
        "flowModal": kwargs.get('flowModal', '')
    }
    return json.dumps(requestParam)


class UniversalContent(RequestBase):
    # 获取universal创建参数

    # 创建universal
    def create_universal(self, requestParam):
        result = self.request(method=URL.saveUniversalContent.method, path=URL.saveUniversalContent.url,
                              data=requestParam)
        return result

    # 查询universal
    def query_universal(self, universa_name='', blockType_list=[]):
        """
        查询素材
        :param blockType_list:
        :param universa_name:
        :return:
        """
        requestParam = {'universalName': universa_name}
        if blockType_list and type(blockType_list) == list:
            requestParam.update(blockType=blockType_list)
        result = self.request(method=URL.queryUniversalContent.method, path=URL.queryUniversalContent.url,
                              data=requestParam)
        return result

    # 更新universal
    def update_universal(self, universal_list, _type=0):
        """
        更新素材
        :param _type:
        :param universal_list:
                [{"universalId": _dict.get('universa_id'),
                "universalName": _dict.get('universa_name'),
                "schema": json.dumps(result_schema),
                "subUniversalId": _dict.get('subUniversal_id', _dict.get('universa_id')),
                "type": _dict.get('type'),
                "blockType": _dict.get('schema').name,
                "flowModal": ""
                }]
        :return:
        """
        requestParam = {
            "data": universal_list,
            "type": _type
        }
        result = self.request(method=URL.updateUniversalContent.method, path=URL.updateUniversalContent.url,
                              data=requestParam)
        return result

    # 删除universal
    def delete_universal(self, universalId):
        """
        删除素材
        :param universa_id:
        :return:
        """
        requestParam = {'universalId': universalId}
        result = self.request(method=URL.deleteUniversalContent.method, path=URL.deleteUniversalContent.url,
                              params=requestParam)
        return result

    def update_campaign_used(self, campaignId, universalIds: list, _type=0):
        """
        更新活动素材关系
        :param campaignId:
        :param universalIds:
        :param _type:
        :return:
        """
        requestParam = {"type": _type, "campaignId": campaignId, "universalIds": universalIds}
        result = self.request(method=URL.updateCampaignUsed.method, path=URL.updateCampaignUsed.url,
                              data=requestParam)
        return result

    def assert_block_in_the_section(self, section_universa_name, block_universa=None):
        """
        判断收藏的block是否在该section中
        :param section_universa_name:
        :param _id:
        :param block_universa_id:
        :param block_universa_name:
        :return:
        """
        result = self.query_universal(universa_name=section_universa_name)
        if result:
            section = result['resultData']['datas'][0]
            schema = json.loads(section['schema'])
        if section['blockType'] == 'Section':
            try:
                assert block_universa == schema['children'][0]['children']
                # if block_universa_id: # assert ListDictUtils.all_in_list(block_universa_id, #
                # [blockUniversalId:ss['universalId'] ) elif block_universa_name: assert ListDictUtils.all_in_list(
                # block_universa_name, [ss['universalName'] for ss in schema['children'][0]['children']]) elif _id:
                # assert ListDictUtils.all_in_list(_id, [ss['id'] for ss in schema['children'][0]['children']])
                print(f"------收藏的block在该section({section_universa_name})中,断言成功------")
            except:
                raise


def get_time():
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


def gen_universal_name(schema):
    schema = schema if isinstance(schema, dict) else schema.value
    if schema['type']:
        return 'Auto-' + schema['type'] + '-' + get_time()
    else:
        return 'Auto-' + generate_UUID(5) + '-' + get_time()


def get_universal_schema(schema, _id, universalId, universalName):
    schema = schema if isinstance(schema, dict) else schema.value
    schema.update(id=_id, universalId=universalId, universalName=universalName)
    return schema


if __name__ == '__main__':
    # _list = [get_universal_schema(BlockSchema.Logo, _id=generate_UUID(9), universalId=generate_UUID(),
    #                               universalName=gen_universal_name(BlockSchema.Logo))]
    # print(json.dumps(_list))
    # print(gen_universal_request_param(generate_UUID(),
    #                                              get_universal_schema(genSection(_list), _id=generate_UUID(9),
    #                                                                   universalId=generate_UUID(),
    #                                                                   universalName=gen_universal_name(
    #                                                                       BlockSchema.Section))))
    sectionUniversalId = generate_UUID()
    sectionUniversalName = gen_universal_name(BlockSchema.Section)
    print(sectionUniversalName)
    block_list = [BlockSchema.Logo]
    block_dict = {}
    result_list = []
    blockUniversalNameList = []
    for block in block_list:
        name = block.name
        block_schema = get_universal_schema(block, _id=generate_UUID(9), universalId=generate_UUID(),
                                            universalName=gen_universal_name(block))
        result_list.append(block_schema)
    print(result_list)
    section_schema = get_universal_schema(genSection(result_list), _id=generate_UUID(9), universalId=sectionUniversalId,
                                          universalName=sectionUniversalName)
    universal_request_param = gen_universal_request_param(sectionUniversalId, section_schema)
    print(universal_request_param)
    head = {
        "cookie": "osudb_appid=SMARTPUSH;osudb_oar=#01#SID0000141BOhqtUqYGMjRho2SIPBeE5o1HNWFHo9q+qttt/jMLf+gRshde7x0NZUgAST4PB4CfSuAa450BCuCZf6pwolP1vXs/cF+6e/snBhESLvofXaxDaIFN9swZq4Np2xBc4uw6R4V58uWjrwg+s8XTLVv;osudb_subappid=1;osudb_uid=4213785247;ecom_http_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjU1OTg0NzQsImp0aSI6ImU0YzAyZjcxLWQ4NDktNDZlYS1iNzNmLTY1YjU0YTc3MTJjZCIsInVzZXJJbmZvIjp7ImlkIjowLCJ1c2VySWQiOiI0MjEzNzg1MjQ3IiwidXNlcm5hbWUiOiIiLCJlbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmVhcHAuY29tIiwidXNlclJvbGUiOiJvd25lciIsInBsYXRmb3JtVHlwZSI6Nywic3ViUGxhdGZvcm0iOjEsInBob25lIjoiIiwibGFuZ3VhZ2UiOiJ6aC1oYW5zLWNuIiwiYXV0aFR5cGUiOiIiLCJhdHRyaWJ1dGVzIjp7ImNvdW50cnlDb2RlIjoiQ04iLCJjdXJyZW5jeSI6IkpQWSIsImN1cnJlbmN5U3ltYm9sIjoiSlDCpSIsImRvbWFpbiI6InNtYXJ0cHVzaDQubXlzaG9wbGluZXN0Zy5jb20iLCJsYW5ndWFnZSI6ImVuIiwibWVyY2hhbnRFbWFpbCI6ImZlbGl4LnNoYW9Ac2hvcGxpbmUuY29tIiwibWVyY2hhbnROYW1lIjoiU21hcnRQdXNoNF9lYzJf6Ieq5Yqo5YyW5bqX6ZO6IiwicGhvbmUiOiIiLCJzY29wZUNoYW5nZWQiOmZhbHNlLCJzdGFmZkxhbmd1YWdlIjoiemgtaGFucy1jbiIsInN0YXR1cyI6MCwidGltZXpvbmUiOiJBc2lhL01hY2FvIn0sInN0b3JlSWQiOiIxNjQ0Mzk1OTIwNDQ0IiwiaGFuZGxlIjoic21hcnRwdXNoNCIsImVudiI6IkNOIiwic3RlIjoiIiwidmVyaWZ5IjoiIn0sImxvZ2luVGltZSI6MTc2MzAwNjQ3NDQzNywic2NvcGUiOlsiZW1haWwtbWFya2V0IiwiY29va2llIiwic2wtZWNvbS1lbWFpbC1tYXJrZXQtbmV3LXRlc3QiLCJlbWFpbC1tYXJrZXQtbmV3LWRldi1mcyIsImFwaS11Yy1lYzIiLCJhcGktc3UtZWMyIiwiYXBpLWVtLWVjMiIsImZsb3ctcGx1Z2luIiwiYXBpLXNwLW1hcmtldC1lYzIiXSwiY2xpZW50X2lkIjoiZW1haWwtbWFya2V0In0.erTiG4r364sutySNgx8X1rmrAjFsyfoe3UIUZ6J9e-o;",
        "Content-Type": "application/json", "accept-language": "zh-CN"}
    universal = UniversalContent(headers=head, host='https://test.smartpushedm.com/bff/api-sp-market-ec2')
    try:
        universal.create_universal(requestParam=universal_request_param)
        universal.assert_block_in_the_section(sectionUniversalName, result_list)
    except:
        raise
    finally:
        universal.delete_universal(sectionUniversalId)
