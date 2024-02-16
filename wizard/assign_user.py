# -*- coding: utf-8 -*-
from datetime import datetime
import json
import requests
from odoo import models, fields, api
import xlsxwriter
import os
import os.path


class AssignUserWizard(models.TransientModel):
    _name = "assign.to.user.wizard"
    _description = "Assign User Wizard"

    project_id = fields.Many2one('smart.meters', string='Project ID')
    username = fields.Many2one('proj.users', string='Username')
    action_type = fields.Selection(
        [('assign_user', 'Assign User'), ('cancel', 'Bulk Cancel')],
        string='Actions Type')
    production_type = fields.Selection(
        [('full', 'HC Full'), ('main_splice', 'Main Splice'), ('main_cabling', 'Main Cabling')
            , ('ojo', 'OJO')], string='Production Type')
    # not usable
    main_projects = fields.Selection([('ftk', 'FTK'), ('zain', 'ZAIN'), ('ojo', 'OJO'), ('nbn', 'NBN')],
                                     string='Main Projects')
    sub_projects = fields.Selection(
        [('hc', 'HC'), ('hp', 'HP'), ('ms_hc', 'MS_HC'), ('ms_hp', 'MS_HP'), ('ms_hp', 'MS_HP'),
         ('hc_micro', 'HC_MICRO'), ('hc_aerial', 'HC_AERIAL'), ('ms', 'MS')], string='Sub Projects')
    ftk_hc_job_type = fields.Selection([('full', 'Full Job'), ('dig', 'Digging')], string='Job Type')
    ftk_hp_job_type = fields.Selection(
        [('main_cab', 'Main Cabling'), ('cab_splice', 'Drop Cabling & BEP Splicing'), ('main_splice', 'Main Splicing')],
        string='Job Type')
    ftk_ms_job_type = fields.Selection([('full', 'Full Job')], string='Job Type')
    zain_hcmicro_job_type = fields.Selection([('full', 'Full Job'), ('dig', 'Digging')], string='Job Type')
    zain_hcaerial_job_type = fields.Selection([('full', 'Full Job')], string='Job Type')
    ftk_hc_full_job_type = fields.Selection(
        [('indoor', 'Indoor'), ('outdoor', 'Outdoor'), ('splicing_bep', 'Splicing Bep'),
         ('splicing_joint', 'Splicing Joint')], string='Job Type')
    ftk_hc_dig_job_type = fields.Selection([('dig', 'Digging')], string='Job Type')
    ftk_ms_hc_full_job_type = fields.Selection([('cabling', 'Cabling'), ('splicing', 'Splicing')], string='Job Type')
    ftk_hp_drop_bep_job_type = fields.Selection([('cabling', 'Cabling'), ('splicing', 'Splicing')], string='Job Type')
    ftk_hp_main_splice_job_type = fields.Selection([('splicing', 'Splicing')], string='Job Type')
    zain_hcmicro_full_job_type = fields.Selection(
        [('cabling', 'Cabling'), ('splicing', 'Splicing'), ('blowing', 'Blowing')], string='Job Type')
    zain_hcmicro_dig_job_type = fields.Selection([('dig', 'Digging')], string='Job Type')
    zain_hcaerial_full_job_type = fields.Selection(
        [('cab_outdoor', 'Outdoor Cabling'), ('cab_indoor', 'Indoor Cabling'), ('splicing', 'Splicing'),
         ('splicing_fdt', 'Splicing FDT')], string='Job Type')

    def send_notification(self, user, token, number):
        serverToken = 'AAAAgZMZAng:APA91bEhhFQ0OzxsdRYuJ-qSz5pBDSqKYve86ismrr9LdBkdf4Hw4pHF2tW4c8-4YqL7XwtFO3XYYsX1yvawob86FwrSSXKfYynW1tx-BhpkpYkB22q3elWo82aePW2qct-KDZ-_5sy1'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + serverToken,
        }
        body = {
            'notification': {
                'title': "مشروع جديد",
                'body': "مشروع جديد قيد التنفيذ رقم : {0}".format(number),
            },
            'priority': 'high',
            'data': {
                'title': "مشروع جديد",
                'body': "مشروع جديد قيد التنفيذ رقم : {0}".format(number),
                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
            },
            'to': "{0}".format(token)
        }
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        print(response.json())
        self.env['users.notification'].create({
            'user_id': user,
            'name': "مشروع جديد",
            'body': "مشروع جديد قيد التنفيذ رقم : {0}".format(number),
            'project_id' : False,
            'response': "Date : " + str(datetime.now()) + " ,status : " + str(
                response.status_code) + " , response result : " + str(response.json()),
        })

    def assign_user_action(self):
        if self.action_type == 'assign_user':
            for project_id in self._context.get('active_ids'):
                project = self.env['smart.meters'].search([('id', '=', project_id)])
                if project.state in ('draft', 'need_reassigned'):
                    project.state = "assigned"
                    project.assigned_user = self.username
                    project.assign_date = datetime.now()
                    self.env['assigned.users.history'].create({
                        'smart_meter_id': project.id,
                        'project_id': False,
                        'user_id': self.username.id,
                    })

                    self.send_notification(self.username.id, self.username.fcm_token, project.name)
        elif self.action_type == 'cancel':
            for project_id in self._context.get('active_ids'):
                project = self.env['smart.meters'].search([('id', '=', project_id)])
                project.state = "cancelled"

