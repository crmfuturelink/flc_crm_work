from odoo import models, fields, api


class FlcStudent(models.Model):
    _name = 'flc.student'
    _description = 'Student Record'
    _rec_name = 'name'
    _order = 'sequence_number desc'

    sequence_number = fields.Char(string="Student ID", required=True, readonly=True, default='New', copy=False)
    name = fields.Char(string="Full Name", required=True)
    birth_date = fields.Date(string="Date of Birth", required=True)
    education_details = fields.One2many('flc.student.education', 'student_id', string="Education Details")

    # creat a examselection filed with IELTS PTE DUOLINGO TOEFL CAEL CELPIP
    exam_name = fields.Selection([('IELTS', 'IELTS'), ('PTE', 'PTE'), ('DUOLINGO', 'DUOLINGO'),
                             ('TOEFL', 'TOEFL'), ('CAEL', 'CAEL'), ('CELPIP', 'CELPIP')], string="Exam")
    test_score = fields.Float(string="Test Score")
    # test_result = fields.Char(string="Test Result")
    test_date = fields.Date(string="Test Date")
    # Upload Certificate

    @api.model
    def create(self, vals):
        print("Self::::::::", self,self._context)
        """Its Create new Sequence when any recorde will generating in FLC student object like 'FL-STU001' """
        if vals.get('sequence_number', 'New') == 'New':
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('flc.student.sequence') or 'FL-STU001'
        return super(FlcStudent, self).create(vals)
    #
    # def copy(self, default=None):
    #     """Generate a new sequence number when duplicating a record"""
    #     default = dict(default or {})
    #     default['sequence_number'] = self.env['ir.sequence'].next_by_code('flc.student.sequence') or 'FL-STU001'
    #     return super(FlcStudent, self).copy(default)


class FlcStudentEducation(models.Model):
    _name = 'flc.student.education'
    _description = 'Student Education Details'

    student_id = fields.Many2one('flc.student', string="Student", required=True)
    level = fields.Selection([('10th', '10th'), ('12th', '12th'), ('bachelor', 'Bachelor'), ('master', 'Master')],
                             string="Level")
    school_name = fields.Char(string="School/Institute Name")
    board_name = fields.Char(string="Board Name")
    marks = fields.Char(string="Marks")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    marksheet_attachment_id = fields.Many2one('ir.attachment', string="Marksheet")
