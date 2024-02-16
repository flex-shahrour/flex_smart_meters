#-*- coding: utf-8 -*-
import datetime
import json
import math
import logging
import requests

from odoo import SUPERUSER_ID, http, _, exceptions
from odoo.http import request

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import xmlrpc.client

_logger = logging.getLogger(__name__)

def error_response(error, msg):
    return {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": 200,
            "message": msg,
            "data": {
                "name": str(error),
                "debug": "",
                "message": msg,
                "arguments": list(error.args),
                "exception_type": type(error).__name__
            }
        }
    }

class LewanSmartMeters(http.Controller):

    @http.route('/api/get/smart/project', type='http', auth='none', methods=['GET'], csrf=False)
    def get_smart_project(self, **params):
        try:
            user_id = params['id']
        except KeyError:
            msg = "`User ID` parameter is not found on GET request"
            raise exceptions.ValidationError(msg)   


        data = []
        projects_info = request.env['smart.meters'].sudo().search([('assigned_user', '=', int(user_id)),('state', '=', 'assigned')], order="id desc")

        for info in projects_info:
            project_info = {}
            # model fields
            project_info['id'] = info.id
            # smart meter fields
            project_info['name'] = info.name
            # main info
            project_info['msdn'] = info.msdn
            project_info['wf'] = info.wf
            project_info['wf_special_code'] = info.wf_special_code
            project_info['appointment_string'] = info.appointment_string
            project_info['assigndate'] = info.assigndate
            project_info['service_type'] = info.service_type
            # customer info
            project_info['cus_name'] = info.cus_name
            project_info['phone'] = info.phone
            project_info['phone_2'] = info.phone_2
            project_info['isp'] = info.isp
            project_info['area'] = info.area
            project_info['address'] = info.address
            # package info
            project_info['speed'] = info.speed
            project_info['structure'] = info.structure
            # feedback
            project_info['activation_state'] = info.activation_state
            project_info['dispatcher_category'] = info.dispatcher_category
            project_info['dispatcher_feedback'] = info.dispatcher_feedback
            # jobs to be done
            project_info['drop_joint_cableN'] = info.drop_joint_cableN
            project_info['drop_joint_cableF'] = info.drop_joint_cableF
            project_info['drop_joint_splicing'] = info.drop_joint_splicing
            project_info['branch_joint_splicing'] = info.branch_joint_splicing
            project_info['prime_joint_splicing'] = info.prime_joint_splicing
            project_info['bep_splicing'] = info.bep_splicing
            project_info['bep_install'] = info.bep_install
            project_info['indoor_cabling'] = info.indoor_cabling
            project_info['active_basic'] = info.active_basic
            project_info['active_deco'] = info.active_deco
            project_info['ucc'] = info.ucc
            project_info['zain_extender'] = info.zain_extender
            data.append(project_info)

        res = {
            "result" : {
                "data": data
            }
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )

    @http.route(
        '/api/complete/smart/project',
        type='json', auth="none", methods=['PUT'], csrf=False)
    def put_smart_project_complete(self, **post):
        try:
            data = post['data']
        except KeyError:
            msg = "`data` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        try:
            materials = post['materials']
        except KeyError:
            msg = "`materials` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        try:
            filter = post['filter']
        except KeyError:
            msg = "`Filter` parameter is not found on PUT request body"
            raise exceptions.ValidationError(msg)

        if 'images' in post:
            images = post['images']
            data['project_images_ids'] = []
            for image in images:
                data['project_images_ids'].append((0,0,image))

        data['project_material_ids'] = []
        for line in materials:
            if line['qty'] != 0:
                data['project_material_ids'].append((0,0,line))
        project = request.env['smart.meters'].sudo().search([('id', '=', filter['id'])])

        inv_data = {}
        #Delivery Orders Operations Types id
        inv_data['picking_type_id'] = 2
        inv_data['location_dest_id'] = 5
        user_location_id = request.env['proj.users'].sudo().search([('id', '=', project.assigned_user.id)])
        inv_data['location_id'] = user_location_id.location_id.id
        inv_data['move_line_ids_without_package'] = []
        for inv_line in materials:
            if inv_line['qty'] != 0:
                product_info = {}
                product_info['location_id'] = user_location_id.location_id.id
                product_info['location_dest_id'] = 5
                product_info['product_id'] = int(inv_line['product_id'])
                product_info['qty_done'] = int(inv_line['qty'])
                lot_production_id = request.env['stock.production.lot'].sudo().search([('name', '=', inv_line['note']), ('product_id', '=', int(inv_line['product_id']))])
                # lot_production_id = request.env['stock.lot'].sudo().search([('name', '=', inv_line['note']), ('product_id', '=', int(inv_line['product_id']))])
                if lot_production_id:
                    #product_info['lot_ids'] = [(4, [lot_production_id.id])]
                    product_info['lot_id'] = lot_production_id.id

                product = request.env['product.product'].sudo().search([('id', '=', int(inv_line['product_id']))])
                product_info['product_uom_id'] = product.uom_id.id
                inv_data['move_line_ids_without_package'].append((0,0,product_info))

        if len(inv_data['move_line_ids_without_package']) > 0:
            inv_record = request.env['stock.picking'].with_user(SUPERUSER_ID).create(inv_data)
            inv_record.action_confirm()
            inv_record.button_validate()

        data['state'] = 'completed'
        data['complete_date'] = datetime.datetime.utcnow()
        record = project.with_user(SUPERUSER_ID).write(data)
        return project.id

    # done.
    @http.route('/api/get/smart/project/complete', type='http', auth='none', methods=['GET'], csrf=False)
    def get_smart_project_complete(self, **params):
        try:
            user_id = params['id']
        except KeyError:
            msg = "`User ID` parameter is not found on GET request"
            raise exceptions.ValidationError(msg)   


        data = []
        projects_info = request.env['smart.meters'].sudo().search([('assigned_user', '=', int(user_id)),('state', '=', 'completed')], order="id desc")

        for info in projects_info:
            project_info = {}
            # model fields
            project_info['id'] = info.id
            # smart meter fields
            project_info['name'] = info.name
            # main info
            project_info['msdn'] = info.msdn
            project_info['wf'] = info.wf
            project_info['wf_special_code'] = info.wf_special_code
            project_info['appointment_string'] = info.appointment_string
            project_info['assigndate'] = info.assigndate
            project_info['service_type'] = info.service_type
            # customer info
            project_info['cus_name'] = info.cus_name
            project_info['phone'] = info.phone
            project_info['phone_2'] = info.phone_2
            project_info['isp'] = info.isp
            project_info['area'] = info.area
            project_info['address'] = info.address
            # package info
            project_info['speed'] = info.speed
            project_info['structure'] = info.structure
            # feedback
            project_info['activation_state'] = info.activation_state
            project_info['dispatcher_category'] = info.dispatcher_category
            project_info['dispatcher_feedback'] = info.dispatcher_feedback
            # jobs to be done
            project_info['drop_joint_cableN'] = info.drop_joint_cableN
            project_info['drop_joint_cableF'] = info.drop_joint_cableF
            project_info['drop_joint_splicing'] = info.drop_joint_splicing
            project_info['branch_joint_splicing'] = info.branch_joint_splicing
            project_info['prime_joint_splicing'] = info.prime_joint_splicing
            project_info['bep_splicing'] = info.bep_splicing
            project_info['bep_install'] = info.bep_install
            project_info['indoor_cabling'] = info.indoor_cabling
            project_info['active_basic'] = info.active_basic
            project_info['active_deco'] = info.active_deco
            project_info['ucc'] = info.ucc
            project_info['zain_extender'] = info.zain_extender

            project_info['materials'] = []
            for item in info.project_material_ids:
                item_info = {}
                item_info['product'] = item.product_id.name
                item_info['qty'] = item.qty
                item_info['note'] = item.note
                project_info['materials'].append(item_info)

            data.append(project_info)

        res = {
            "result" : {
                "data": data
            }
        }
        return http.Response(
            json.dumps(res),
            status=200,
            mimetype='application/json'
        )
