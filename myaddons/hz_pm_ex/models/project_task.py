# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, UserError


class HarProjectTask(models.Model):
    _inherit = 'project.task'
    _description = "协同工作"

    cooperator_ids = fields.Many2many('res.partner', string='协同工作者', track_visibility='onchange')
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, track_visibility='onchange', required=True)
    description = fields.Html(string='Description', required=True)

    # 1.修改任务的协助人或者负责人的时候，推送任务到企业微信
    # 2.修改状态的时候，父子任务之间限制。a.父任务完成了子任务才能完成 b.父任务已经完成的状态下，子任务不允许变成非完成状态
    @api.multi
    def write(self, values):
        task_type_name = self.env['project.task.type'].browse(values.get('stage_id')).name
        if values.get('stage_id'):
            if self.child_ids and task_type_name == 'Finished':
                result = any([i for i in self.child_ids if i.stage_id.name != 'Finished'])
                if result:
                    raise UserError(_("还有子任务没完成！"))
            elif self.parent_id:
                if self.parent_id.stage_id.name == 'Finished' and self.stage_id.name == 'Finished':
                    raise UserError(_("父任务已经完成！"))
        res = super(HarProjectTask, self).write(values)

        if values.get('cooperator_ids') or values.get('user_id'):
            import re
            from wechatpy.exceptions import WeChatClientException
            from odoo.addons.oejia_wx.rpc import corp_client
            from odoo.http import request
            import json
            import pytz

            entry = corp_client.corpenv(self.env)
            tz = self.env.user.tz or 'Asia/Chongqing'
            local_tz = pytz.timezone(tz)
            for item in self:
                task_object = self.env['project.task'].sudo().browse(self.id)

                description = ''
                description += '【当前状态】：%s\n' % task_object.stage_id.name
                description += '【任务名称】：%s \n' % task_object.name
                description += '【项目名称】：%s\n' % task_object.project_id.name
                description += '【截至时间】：%s\n' % task_object.date_deadline
                description += '【负责人】：%s\n' % task_object.user_id.name
                if task_object.cooperator_ids:
                    description += '【协助人】：%s\n' % str([i.name for i in task_object.cooperator_ids])
                # description += '【新协同者】：%s\n' % str(values.get('cooperator_ids')[])

                # userid = task_object.user_id.partner_id.wxcorp_user_id.userid
                # li = []
                # li.append(userid)
                title = '协同工作任务提醒 %s' % (
                    datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)).strftime(
                    '%m%d %H:%M')
                url = str(request.httprequest.headers.get('Host')) + '/open/model/%s/%d' % (
                    'project.task', item.id)
                userid = task_object.user_id.partner_id.wxcorp_user_id.userid
                if userid:
                    entry.client.message.send_text_card(entry.current_agent, userid, title, description, url, "详情")
                if values.get('cooperator_ids'):
                    for i in values.get('cooperator_ids')[0][2]:
                        part = item.env['res.partner'].browse(i)
                        userid2 = part.wxcorp_user_id.userid
                        if userid2:
                            entry.client.message.send_text_card(entry.current_agent, userid2, title, description, url,
                                                                "详情")
        return res

    # 创建任务的时候，推送任务到企业微信中
    @api.model
    def create(self, values):
        res = super(HarProjectTask, self).create(values)
        # if values.get('cooperator_ids'):
        # Add code here
        import re
        from wechatpy.exceptions import WeChatClientException
        from odoo.addons.oejia_wx.rpc import corp_client
        from odoo.http import request
        import json
        import pytz
        entry = corp_client.corpenv(self.env)
        tz = self.env.user.tz or 'Asia/Chongqing'
        local_tz = pytz.timezone(tz)
        for item in res:
            task_object = self.env['project.task'].sudo().browse(res.id)

            description = ''
            description += '【当前状态】：%s\n' % task_object.stage_id.name
            description += '【任务名称】：%s \n' % task_object.name
            description += '【项目名称】：%s\n' % task_object.project_id.name
            description += '【截至时间】：%s\n' % str(task_object.date_deadline)
            description += '【负责人】：%s\n' % task_object.user_id.name
            if task_object.cooperator_ids:
                description += '【协同者】：%s\n' % str([i.name for i in task_object.cooperator_ids])
            title = '协同工作任务提醒 %s' % (
                datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)).strftime(
                '%m%d %H:%M')
            url = str(request.httprequest.headers.get('Host')) + '/open/model/%s/%d' % (
                'project.task', item.id)
            userid = task_object.user_id.partner_id.wxcorp_user_id.userid
            if userid:
                entry.client.message.send_text_card(entry.current_agent, userid, title, description, url, "详情")

            if values.get('cooperator_ids'):
                for i in values.get('cooperator_ids')[0][2]:
                    part = item.env['res.partner'].browse(i)
                    userid2 = part.wxcorp_user_id.userid
                    if userid2:
                        entry.client.message.send_text_card(entry.current_agent, userid2, title, description, url, "详情")

        return res

    # 推送企业微信过期任务提醒，主要是在安排的动作中调用
    @api.multi
    def send_project_task_dateline_message(self):
        import re
        from wechatpy.exceptions import WeChatClientException
        from odoo.addons.oejia_wx.rpc import corp_client
        from odoo.http import request
        import json
        import pytz

        # 推送微信任务过期提醒
        sqlstr = '''
            SELECT 
                    T.id task_id,
                    T.date_deadline,
                    T.NAME task_name,
                    P.NAME project_name,
                    T.date_deadline,
                    TO_CHAR( NOW(), 'YYYY-MM-DD' ) THISDATETIME,
                    (
                    EXTRACT ( DAY FROM T.date_deadline ) - EXTRACT (
                DAY 
                FROM
                    now())) num,
                    r."login",
                    r.ID user_id,
                    pt.NAME type_name ,
                    t.project_id
                FROM
                    project_task
                    T LEFT JOIN project_project P ON P.ID = T.project_id
                    LEFT JOIN res_users r ON r.ID = T.user_id
                    LEFT JOIN project_task_type pt ON pt.ID = T.stage_id 
                WHERE
                    TO_CHAR( T.date_deadline, 'YYYY-MM-DD' ) < TO_CHAR( NOW(), 'YYYY-MM-DD' ) and pt.NAME!='Finished' 
                    and pt.NAME!='Pending' and pt.NAME!='Cancel'
                    '''
        self.env.cr.execute(sqlstr)
        sql_results = self.env.cr.dictfetchall()
        if sql_results:
            entry = corp_client.corpenv(self.env)
            tz = self.env.user.tz or 'Asia/Chongqing'
            local_tz = pytz.timezone(tz)
            for item in sql_results:
                task_object = self.env['project.task'].sudo().browse(item['task_id'])

                description = ''
                description += '【当前状态】：%s\n' % str(item['type_name'])
                description += '【任务名称】：%s \n' % item['task_name']
                description += '【项目名称】：%s\n' % item['project_name']
                description += '【截至时间】：%s\n' % str(item['date_deadline'])
                description += '【负责人】：%s\n' % task_object.user_id.name
                if task_object.cooperator_ids:
                    description += '【协助人】：%s\n' % str([i.name for i in task_object.cooperator_ids])

                userid = task_object.user_id.partner_id.wxcorp_user_id.userid

                title = '过期任务提醒 %s' % (datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(local_tz)).strftime(
                    '%m%d %H:%M')
                url = str(request.httprequest.headers.get('Host')) + '/open/model/%s/%d' % (
                    'project.task', item['task_id'])
                if userid:
                    entry.client.message.send_text_card(entry.current_agent, userid, title, description, url, "详情")
                if task_object.cooperator_ids:
                    for i in task_object.cooperator_ids:
                        userid2 = i.wxcorp_user_id.userid
                        if userid2:
                            entry.client.message.send_text_card(entry.current_agent, userid2, title, description, url,
                                                                "详情")



