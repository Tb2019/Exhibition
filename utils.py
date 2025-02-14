# -*- coding: utf-8 -*-
import json
import re

import pymysql
import requests
import os

siliconflow_key = os.getenv('siliconflowkey')

def get_resp_siliconflow():
    url = "https://api.aicnn.cn/v1/chat/completions"
    prompt = """
                ##角色
                    你是一位会展信息提取专家，善于从html格式的有关会展的文本中提取需要的信息。
                ##技能
                    #技能1：提取主办单位
                        提取出主办单位的名称,没有则为''
                    #技能2：提取联系方式
                        提取联系人，联系电话和邮箱信息，没有则为''。可能有多个联系方式。
                ##输出格式
                    -使用json格式输出。
                    -样例：{"主办单位":"", "联系方式":[{"联系人":"", "电话":"['','',...]", "邮箱":"['','',...]"},...]}
                    -严格按照样例的格式，严禁篡改key如"c电话"
    """

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": None
            }
        ],
        "stream": False,
        "max_tokens": 4096,
        # "stop": ["null"],
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0,
        "n": 1,
        "response_format": {"type": "json_object"},
        "tools": [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
    }
    headers = {
        "Authorization": "Bearer " + siliconflow_key,
        "Content-Type": "application/json"
    }

    def inner(content):
        payload['messages'][1]['content'] = content
        response = requests.request("POST", url, json=payload, headers=headers)
        return response.json()
    return inner

class Saver:
    config = json.loads(os.getenv('comp_local_sql_config'))
    db = 'alpha_search_update'
    table = 'search_exhibition'

    def __init__(self, ):
        # self.host = self.config['host']
        # self.port = self.config['port']
        # self.password = self.config['password']
        self.conn = pymysql.connect(db=self.db,**self.config)
        self.cursor = self.conn.cursor()

    def save(self, item):
        keys = ','.join(item.keys())
        values = ','.join(['%s'] * len(item))

        sql = f'insert into {self.table} ({keys}) values({values})'
        try:
            self.cursor.execute(sql, tuple(item.values()))
            self.conn.commit()
            print('存储成功')
        except Exception as e:
            self.conn.rollback()
            print('存储失败', e)

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    content = """
    <div class="exhi-content">
                    <div>
						<div style="text-align: center;">　　<strong>山东鲁南</strong><strong>苏北</strong><strong>装备盛会 &nbsp;总规模</strong><strong>3</strong><strong>0000平方米</strong><br>&nbsp;</div><div style="text-align: center;">　　<strong>202</strong><strong>5</strong><strong>第</strong><strong>十八</strong><strong>届</strong><strong>中国</strong><strong>临沂工业装备</strong><strong>博览会</strong><br>&nbsp;</div><div style="text-align: center;">　　<strong>第18届临沂机床及工模具展</strong><strong>‖</strong><strong>第18届临沂自动化技术及智能装备展</strong><br>&nbsp;</div><div style="text-align: center;">　　<strong>时间：202</strong><strong>5</strong><strong>年</strong><strong>5</strong><strong>月</strong><strong>23</strong><strong>日-</strong><strong>25</strong><strong>日 &nbsp;&nbsp;地点：山东临沂国际会展中心</strong></div><div>&nbsp;</div><div>　　</div><div style="text-align: left;">&nbsp;</div><div style="text-align: left;">　　<strong>主办单位：</strong>中国国际贸易促进委员会临沂市委员会<br>&nbsp;</div><div style="text-align: left;">　　<strong>承办单位</strong><strong>：</strong>&nbsp;山东恒展国际会展有限公司<br>&nbsp;</div><div style="text-align: left;">　　<strong>协办单位：</strong>河东机电市场(机床市场)&nbsp;临沂豪德五金机电城、临沂市机械产业工作专班、济宁市机械行业商会 &nbsp;临沂市机床协会</div><div>&nbsp;</div><div>　　<strong>【</strong><strong>展会概述</strong><strong>】</strong><br>&nbsp;</div><div>　　临沂工业装备博览会(临沂机床展)已经连续召开 17&nbsp;届，展会一年一届，是鲁南苏北地区工业行业盛会。临沂工博会依托本地工程机械、五金机械、木工机械、园林机械以及植保机械等当地优势产业，每届展会都吸引了大批高精尖先进品牌和中低端设备企业实地展出。2025第18届临沂工业装备博览会定档于2025&nbsp;年5月23-25号，计划展出面积30000平，设立标准展位1000个，展商500家，我们致力于专业观众精准邀约，通过抖音头条朋友圈等线上宣传、同行展会宣传、地推登门拜访、大巴车免费接送采购商等多种方式，争取把临沂工博会打造成行业品牌展会。<br>&nbsp;</div><div>　　<strong>【</strong><strong>展会优势</strong><strong>】</strong><br>&nbsp;</div><div>　　一、工业优势：2022年，临沂就提出“实施先进工业强市战略，让工业成为现代化建设的中流砥柱”。2023年，临沂规上工业总产值突破8000亿元；八大传统产业产值增长11.4%，千亿级产业达到3个、百亿级企业达到10家；临沂的先进工业“脊梁”加速挺起。<br>&nbsp;</div><div>　　二、市场优势：临沂市拥有各类批发市场 100 多个，其中，工业品市场有工业品采购市场、临沂激光产业园、金科临沂智能制造科技城、河东机床市场、临沂模具产业园、临沂钢材市场(江北钢材市场、林丰钢材市场、美鑫钢材市场、钢材物流城、临港不锈钢基地)、临工产业园、豪德五金机电城、临沂五金城、北方五金建材城、香江五金机电市场、华东五金市场、蓝田五金市场、东立五金城、站前商场(鑫鼎泰)、工程机械产业园等。临沂是全国各地厂工业厂商进驻北方市场的必选之地，也是国内最重要的工业产品集散地之一，临沂工业品市场在全国十大工业品市场中名列前三。<br>&nbsp;</div><div>　　三、交通优势：临沂位于长三角和环渤海经济圈的过渡地带，有“物流之都”美誉， 交通十分便利，临沂机场、临沂高铁、京沪高速、长深高速以及市区高架桥极大地方便商贸通行，临沂已成为连接环渤海工业区与长三角工业区的交通枢纽。<br>&nbsp;</div><div>　　<strong>【</strong><strong>历届回顾</strong><strong>】</strong><br>&nbsp;</div><div>　　机床展商:威达精工、海天精工、广东佳盟子、宝鸡机床、临沂金星机床、瑞铁机床、迪格重工、青岛云科、扬州顺儒、昆山瑞钧、泽诚数控、江南精机、万利精机、浙江锯力煌、浙江晨龙、杭州优锯、江苏金凯达、浙江锐力、浙江中德利、浙江阿波罗、大英新代、苏机、<br>&nbsp;</div><div>　　深圳捷甬达、玖野数控、三菱刀具、株洲硬质合金、中环机床。<br>&nbsp;</div><div>　　激光展商:镭戈斯、中山艺翔、镭鸣激光、宏牛激光、、锐捷激光、立为激光、德锐刻激光、河北国宏激光、临沂乐狄激光、河北鸿楠、临沂睿雕、大赫激光、大威激光、山东飞速激光、青岛通用激光、济南精鑫、青岛领航者、金强激光等<br>&nbsp;</div><div>　　机器人展商:卡诺普机器人、ABB机器人、库卡机器人、钱江机器人、伯朗特机器人、上海欢颜机器人、临沂易云、山东北工、迈德尔机器人、帅科机器人、山东博裕机器人、伊唯特机器人、迈德尔机器人、山森数控、大匠机器人等。<br>&nbsp;</div><div>　　自动化展商:英威腾、施耐德、西门子、中国台湾鼎翰传动、苏州明纬、欧姆龙、山东元润、浙江欧迈特、安贝特变频器、深圳易控、东莞卓兰、上海开民、南京开通、青岛科润、台达变频器、海菱电器等。<br>&nbsp;</div><div>　　<strong>【参展范围】</strong><br>&nbsp;</div><div>　　一、各类机床及功能部件<br>&nbsp;</div><div>　　各类加工中心、金属切削机床、金属成型机床、具体表现为车床、铣床、镗床、镗铣床、磨床、钻床、锯床、拉床、刨床、雕刻机、电加工/线切割机床、齿轮加工机床、专用机床等;机床电器、刀具、量具量仪、卡具、刃具、工装、夹具、卡盘、磨料磨具、检验和测量设备、模具技术、五金模具、塑胶模具、金属切削油、润滑油、机床附件等;<br>&nbsp;</div><div>　　二、激光设备及钣金加工设备<br>&nbsp;</div><div>　　激光切割机、激光打标机、激光焊接机、激光雕刻机、激光设备配件、电加工及激光加工等特种加工机床、激光喷码技术等、激光辅助设备及配件、激光和光导发光元件等，金属切割及焊接设备、水射流技术、冲压机床、液压机、剪板机、折弯机、卷板机、弯管机、自动锻机、铆接机、效正效平机、锻造机及周边设备等;<br>&nbsp;</div><div>　　三、工业机器人<br>&nbsp;</div><div>　　焊接机器人、喷涂机器人、码垛机器人、搬运机器人、装配机器人、直角坐标机器人、机器人工作站、机器人解决方案、机器人配件、工业机器人整机、机器人系统集成、机器视觉、机械手等<br>&nbsp;</div><div>　　四、工业自动化<br>&nbsp;</div><div>　　伺服电机、变频器和马达、步进电机、变压器、传动、导轨、减速机、电线及电缆附件、低压开关、继电器、按钮、工业电源、仪器仪表、工业电气系统、工业控制系统、工业自动化软件、接口技术、连接器、低电压开关装置、工业测量及仪器仪表、3D打印技术等;<br>&nbsp;</div><div>　　五、铸造展区<br>&nbsp;</div><div>　　铸钢、铸铁、不锈钢铸件、有色合金铸件、铝铸件、铜铸件、球墨铸件、耐磨铸件等各类铸件；各类熔炼炉，自动浇注机，造型线，制芯中心，混砂机，砂处理设备，砂再生设备，抛丸清理设备，压铸机，低压铸造机等各类铸造设备；铁合金、有色金属、铸造焦、精炼剂、孕育剂、球化剂、蠕化剂、除渣剂、石英砂、覆膜砂、铬铁矿砂等铸造材料；各类铸造仪器与环保设备等：<br>&nbsp;</div><div>　　六、工程机械<br>&nbsp;</div><div>　　挖掘机、装载机械、起重机械、铲运机械、推土机、工程机械、建筑机械、路面机械等设备；<br>&nbsp;</div><div>　　七、动力传动<br>&nbsp;</div><div>　　直线导轨、滚珠丝杠、液压、液力、气动装器、密封产品及生产装备、机械传动、电力传动、轴承、润滑液、相关零部件等;<br>&nbsp;</div><div>　　八、其他机械设备展区：锻压铸造、工程机械、矿山机械、木工机械、农机、园林机械、植保机械、五金机械、环保设备等；<br>&nbsp;</div><div>　　<strong>【展会</strong><strong>宣传</strong><strong>】</strong><br>&nbsp;</div><div>　　1.&nbsp;线上宣传:通过抖音、快手、头条、朋友圈、微信、微博等线上广告进行宣传另外，工博会、工业行业网站、展会网站等行业网站进行线上宣传;<br>&nbsp;</div><div>　　2.&nbsp;线下宣传:组委会成立观众邀约小组，对临沂以及各省市工业市场、产业园派送展会门票、展会邀请函邀请其到临沂工博会现场购机洽谈业务；<br>&nbsp;</div><div>　　3.&nbsp;大大巴车接送采购商:与各大工业品市场、工业园区、行业协会合作，通过大巴车免费接送的方式组团参观展会;<br>&nbsp;</div><div>　　4.&nbsp;户外广告宣传:通过高速路广告、市场广告、公交车广告、出租车广告、户外LED屏、户外墙体粉刷广告等多种方式宣传展会;<br>&nbsp;</div><div>　　5.&nbsp;专业观众数据库宣传:公司有数十万专业观众数据库、通过短信群发、电话邀请、邀请函邮寄等方式邀请参观展会；<br>&nbsp;</div><div>　　6.&nbsp;同行展会宣传:观众邀约小组对同行展会进行实地派发宣传资料宣传展会:<br>&nbsp;</div><div>　　7.&nbsp;活动宣传:有计划的举办多场展会推介会、新闻发布会、行业交流会组织参观<br>&nbsp;</div><div>　　8.&nbsp;政府、行业协会宣传:临沂市贸促会、临沂市机床协会、临沂模具协会、临沂焊接机械商会、济宁机械商会等部门组织会员单位参观临沂工博会。<br>&nbsp;</div><div>　　<strong>【</strong><strong>展位</strong><strong>收</strong><strong>费</strong><strong>】</strong><br>&nbsp;</div><div>　　★标准展位：国内企业：3M×3M=9平方&nbsp;&nbsp;6800元人民币(双开口加收500元角位费)<br>&nbsp;</div><div>　　标准展位配备：三面展板、楣板、一张洽谈桌、两把折叠椅、220V电源插座。<br>&nbsp;</div><div>　　★特装展位：国内企业：600元/平方米 (不少于36平方米)<br>&nbsp;</div><div>　　(注：特装管理费收费标准是：桁架结构10元/平，木质结构：15元/平。)<br>&nbsp;</div><div>　　<strong>【参展手续】</strong><br>&nbsp;</div><div>　　1、即时起报名，参展商须申请展位并填写《参展申请表》，由负责人签字及公司盖章后，传真或邮寄至承办单位，承办单位将根据参展报名及收到合同定金款的先后次序安排及确认展位。<br>&nbsp;</div><div>　　2、展位租金及广告费用等一律实行预收，参展商在签定参展合同或广告项目合同后，应于3日内将参展费用汇入承办单位帐户，并将银行汇款底单传真至承办单位。逾期承办单位将不予保留展位或广告版位。<br>&nbsp;</div><div>　　3、参展商应按展览会规定的范围申报及展示其展品，如申报展品或参展展品有违展览会展品范围的规定，承办机构有权拒绝或取消其参展资格，所交参展费用概不退还。<br>&nbsp;</div><div>　　4、会务接待、住宿、展品托运等请见《布展通知》。<br>&nbsp;</div><div>　　<strong>大会组委会联系方式</strong><strong>：</strong><br>&nbsp;</div><div>　　山东恒展国际会展有限公司<br>&nbsp;</div><div>　　地址:临沂市兰山区齐鲁大厦901室<br>&nbsp;</div><div>　　电话：徐花17753965949(微信号)<br>&nbsp;</div><div>　　固定电话：0539-2030048<br>&nbsp;</div><div>　　网站：http://gbh.hzizh.com<br>&nbsp;</div>
					</div>
                </div>
    """
    res = get_resp_siliconflow()(content)['choices'][0]['message']['content']
    res = re.sub(r'^.*?(\{.*}).*?$', r'\1', res, flags=re.S)
    # res = re.sub(r'(,\s*)(?=}$)', '', res, flags=re.S)
    enf = json.loads(res)
    print(enf, type(enf))
