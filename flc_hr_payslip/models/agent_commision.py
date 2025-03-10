from odoo import models, fields, api, Command

class AgentCommission(models.Model):
    _name = 'agent.commission'
    _description = 'Agent Commission'

    agent_commission_type = fields.Selection(
        selection=[('percentage', 'Percentage'), ('fixed', 'Fixed'), ('slab', 'Slab')],
        string="Agent Commission Type",
        compute="_compute_commission",
        store=True,
        readonly=False
    )
    commission_amount = fields.Float(string="Total Commission", compute="_compute_commission", store=True)
    student_ids = fields.One2many('flc.student', 'agent_id', string="Students")

    @api.depends('institute_id', 'student_ids')
    def _compute_commission(self):
        """Compute Agent Commission"""
        for record in self:
            record.agent_commission_type = record.institute_id.agent_commission_type
            record.agent_fixed_price = record.institute_id.agent_fixed_price
            record.agent_percentage_price = record.institute_id.agent_percentage_price
            record.is_bonus_commission = record.institute_id.is_bonus_commission

            # Reset values based on commission type
            if record.agent_commission_type == 'percentage':
                record.agent_fixed_price = 0.0
            elif record.agent_commission_type == 'fixed':
                record.agent_percentage_price = 0.0
            elif record.agent_commission_type == 'slab':
                record.agent_percentage_price = 0.0
                record.agent_fixed_price = 0.0

            # Handle Slab-Based Commission
            if record.institute_id.agent_slab_line_ids:
                record.agent_slab_line_ids = [(5, 0, 0)]  # Clear existing records
                record.agent_slab_line_ids += [
                    Command.create({
                        'agent_institute_commission_id': record.id,
                        'no_of_client': line.no_of_client,
                        'type': line.type,
                        'amount': line.amount,
                    }) for line in record.institute_id.agent_slab_line_ids
                ]
            else:
                record.agent_slab_line_ids = False  # No slab data available

            # Bonus Commission
            if record.is_bonus_commission:
                record.bonus_amount = record.institute_id.bonus_amount
                record.bonus_fixed_price = record.institute_id.bonus_fixed_price
                record.bonus_percentage_price = record.institute_id.bonus_percentage_price

                # Reset bonus based on type
                if record.bonus_amount == 'percentage':
                    record.bonus_fixed_price = 0.0
                elif record.bonus_amount == 'fixed':
                    record.bonus_percentage_price = 0.0
                elif record.bonus_amount == 'slab':
                    record.bonus_percentage_price = 0.0
                    record.bonus_fixed_price = 0.0

                # Handle Bonus Slab-Based Commission
                if record.institute_id.bonus_slab_line_ids:
                    record.bonus_slab_line_ids = [(5, 0, 0)]  # Clear existing records
                    record.bonus_slab_line_ids += [
                        Command.create({
                            'agent_institute_commission_id': record.id,
                            'no_of_client': bonus_line.no_of_client,
                            'type': bonus_line.type,
                            'amount': bonus_line.amount,
                        }) for bonus_line in record.institute_id.bonus_slab_line_ids
                    ]
                else:
                    record.bonus_slab_line_ids = False  # No bonus slab data available

            # # Commission Calculation Based on Number of Students
            ### Old Code
            # student_count = len(record.student_ids)
            #
            # if student_count >= 5:
            #     commission_per_student = 1300  # Apply 1300 CAD for all students if count is 5 or more
            # else:
            #     commission_per_student = 1100  # Apply 1100 CAD if less than 5 students
            #
            # record.commission_amount = student_count * commission_per_student

            # Commission Calculation Based on Number of Students
            ## Ranjan Code
            student_count = len(record.student_ids)

            if student_count <= 4:
                record.commission_amount = student_count * 1100  # 1100 CAD per student if count is 4 or less
            else:
                first_four_commission = 4 * 1100  # First 4 students at 1100 CAD
                remaining_commission = (student_count - 4) * 1300  # Remaining students at 1300 CAD
                record.commission_amount = first_four_commission + remaining_commission

