from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class SmartMeters(models.Model):
    _name = 'smart.meters'
    _description = 'Smart Meters'
    _rec_name = 'name'

    # smart meter fields
    sequence = fields.Integer(string='Sequence', index=True, default=1, help="Gives the sequence order", copy=False)
    name = fields.Char(string='Order Reference', default=lambda self: _('New'), copy=False, readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('assigned', 'Assigned'),
                              ('need_reassigned', 'Need To Reassigned'), ('completed', 'Completed'),
                              ('cancelled', 'cancelled')],
                             default='draft')
    # main info
    msdn = fields.Char(string='MSDN')
    wf = fields.Char(string='WF')
    wf_special_code = fields.Char(string='WF Special Code')
    appointment = fields.Datetime(string='Appointment Time')
    appointment_string = fields.Char(string='Appointment String')
    assigndate = fields.Char('Assign Date')
    service_type = fields.Char(string='Service Type')
    # customer info
    cus_name = fields.Char(string="Customer Name")
    phone = fields.Char(string="Phone")
    phone_2 = fields.Char(string="Phone 2 No")
    isp = fields.Char(string="ISP")
    area = fields.Char(string="Area")
    address = fields.Char(string="Address")
    # package info
    speed = fields.Char(string="Speed")
    structure = fields.Char(string="Structure")
    # feedback
    activation_state = fields.Selection([('online', 'Online'), ('not_ready', 'Not Ready')], string='Activation State')
    dispatcher_category = fields.Selection(
        [('Contact Issue', 'Contact Issue'), ('Cancel', 'Cancel'), ('Out Of Coverge', 'Out Of Coverge'),
         ('Out Of Lewan Area', 'Out Of Lewan Area'), ('Sales Issue', 'Sales Issue'),
         ('Owner Objection', 'Owner Objection'), ('Closed Path', 'Closed Path'), ('Need Pole', 'Need Pole'),
         ('Postponed', 'Postponed')
            , ('Need Civil', 'Need Civil'), ('Draft', 'Draft'), ('Waiting FTK', 'Waiting FTK'),
         ('Civil Work Done', 'Civil Work Done')], string='Dispatcher category')

    dispatcher_feedback = fields.Text("Dispatcher feedback")

    # jobs to be done
    drop_joint_cableN = fields.Boolean(string='Drop Joint Cable (Normal)')
    drop_joint_cableF = fields.Boolean(string='Drop Joint Cable (Fast)')
    drop_joint_splicing = fields.Boolean(string='Drop Joint Splicing')
    branch_joint_splicing = fields.Boolean(string='Branch Joint Splicing')
    prime_joint_splicing = fields.Boolean(string='Prime Joint Splicing')
    bep_splicing = fields.Boolean(string='BEP Splicing')
    bep_install = fields.Boolean(string='BEP Installation')
    indoor_cabling = fields.Boolean(string='Indoor Cabling')
    active_basic = fields.Boolean(string='Activation Basic')
    active_deco = fields.Boolean(string='Activation Deco')
    ucc = fields.Boolean(string='UCC')
    zain_extender = fields.Boolean(string='Zain Extender')

    # materials
    project_material_ids = fields.One2many('project.product.line', 'smart_meter_id', string='Materials')

    # Assigned Users History
    assigned_user = fields.Many2one('proj.users', string='Assigned User')
    assigned_users_ids = fields.One2many('assigned.users.history', 'smart_meter_id', string='Assigned User History')
    # feedback
    feedback = fields.Text("Feedback")
    user_response_ids = fields.One2many('user.response', 'smart_meter_id', string='User Response')
    # dates
    create_date = fields.Datetime(string='Create Date', readonly=True)
    assign_date = fields.Datetime(string='Assign Date', readonly=True)
    submit_date = fields.Datetime(string='Submit Date')
    delivery_date = fields.Datetime(string='Delivery Date')
    complete_date = fields.Datetime(string='Complete Date')
    # other info
    technical_code = fields.Char(string='Technical Code')
    parsel_code = fields.Char(string='Parsel Code')
    power_value = fields.Char(string='Power Value')
    street_name = fields.Char(string='Street Name')
    building_number = fields.Char(string='Building Number')
    project_note = fields.Text("Project Note")
    # images
    project_images_ids = fields.One2many('project.images', 'smart_meter_id', string='Images')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'smart.meter.seq')
        if 'appointment_string' in vals:
            print("962110085031")
            print(vals['appointment_string'])
            if vals['appointment_string']:
                datetime_list = vals['appointment_string'].split("-")
                date_list = datetime_list[0].split("/")
                time_list = datetime_list[1].split(":")
                hour = int(time_list[0]) - 3
                if len(str(hour)) == 1:
                    hour = "0" + str(hour)
                vals['appointment'] = date_list[2][:4] + "-" + date_list[1] + "-" + date_list[0] + " " + str(hour) + ":" + time_list[1][:2] + ":00"

        return super(SmartMeters, self).create(vals)



    # def write(self, vals):
    #     if 'assign_date' in vals:
    #         assign_date_string = vals['assign_date']
    #         if assign_date_string:
    #             datetime_list = assign_date_string.split("-")
    #             date_list = datetime_list[0].split("/")
    #             time_list = datetime_list[1].split(":")
    #             hour = int(time_list[0]) - 3
    #             if len(str(hour)) == 1:
    #                 hour = "0" + str(hour)
    #             vals['assigndate'] = date_list[2][:4] + "-" + date_list[1] + "-" + date_list[0] + " " + str(hour) + ":" + time_list[1][:2] + ":00"

    def write(self, vals):
        if 'assign_date' in vals:
            datetime_value = fields.Datetime.from_string(vals['assign_date'])
            datetime_str_default = fields.Datetime.to_string(datetime_value)
            datetime_str_custom = datetime_value.strftime('%d/%m/%Y - %M:%H%p')
            vals['assigndate'] = datetime_str_custom
        if 'appointment' in vals:
            datetime_value = fields.Datetime.from_string(vals['appointment'])
            datetime_str_default = fields.Datetime.to_string(datetime_value)
            datetime_str_custom = datetime_value.strftime('%d/%m/%Y - %M:%H%p')
            print(datetime_str_custom)
            vals['appointment_string'] = datetime_str_custom

        return super(SmartMeters, self).write(vals)

    def cancel_project(self):
        self.state = "cancelled"

    def action_to_assign_user(self):
        return {
            'name': _('Assign User'),
            'type': 'ir.actions.act_window',
            'res_model': 'assign.to.user.wizard',
            'view_mode': 'form',
            # 'view_id': self.env.ref('flex_smart_meters.action_to_assign_user').id,
            'target': 'new',
        }

    @api.onchange('appointment_string')
    def onchange_appointment(self):
        if self.appointment_string:
            datetime_list = self.appointment_string.split("-")
            date_list = datetime_list[0].split("/")
            time_list = datetime_list[1].split(":")
            hour = int(time_list[0]) - 3
            if len(str(hour)) == 1:
                hour = "0" + str(hour)
            convert_date = date_list[2][:4] + "-" + date_list[1] + "-" + date_list[0] + " " + str(hour) + ":" + \
                           time_list[1][:2] + ":00"
            self.appointment = convert_date
        else:
            self.appointment = False

class ProjectProductLine(models.Model):
    _inherit = 'project.product.line'

    smart_meter_id = fields.Many2one('smart.meters', string='smart meter')

class AssignedUsersHistory(models.Model):
    _inherit = 'assigned.users.history'

    smart_meter_id = fields.Many2one('smart.meters', string='smart meter')

class UserResponse(models.Model):
    _inherit = 'user.response'

    smart_meter_id = fields.Many2one('smart.meters', string='smart meter')

class ProjectImages(models.Model):
    _inherit = 'project.images'

    smart_meter_id = fields.Many2one('smart.meters', string='smart meter')




