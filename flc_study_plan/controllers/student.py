from odoo import http
from odoo.http import request
import json


class StudentAPI(http.Controller):

    @http.route('/api/reg-student', type='json', auth='public', methods=['POST'], csrf=False)
    def get_student(self, **kwargs):
        try:
            # Get data from request - use safer approach
            data = {}

            # Try to get JSON data from the request
            try:
                # For newer Odoo versions
                if hasattr(request, 'jsonrequest'):
                    data = request.jsonrequest
                # For older Odoo versions
                else:
                    data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                # If JSON parsing fails, use kwargs
                data = kwargs

            # Extract data from either source
            name = data.get('name')
            print("name:::::",name)
            dob = data.get('dob')
            print("dob:::::", dob)

            if not name or not dob:
                return {'success': False, 'error': 'Missing name or date of birth'}

            # Search for the student in the database
            student = request.env['flc.student'].sudo().search([('name', '=', name), ('birth_date', '=', dob)], limit=1)

            if not student:
                # Create a new student record if not found
                student = request.env['flc.student'].sudo().create({
                    'name': name,
                    'birth_date': dob
                })
                return {'success': True, 'message': 'Student created successfully', 'student_id': student.id}

            # Prepare response data
            student_data = {
                'student_id': student.id,
                'name': student.name,
                'dob': student.birth_date
            }

            return {'success': True, 'student': student_data}

        except Exception as e:
            import traceback
            return {'success': False, 'error': str(e), 'traceback': traceback.format_exc()}