"""
Context processor for school admin views
"""

def admin_context(request):
    """Add admin-related context to all templates"""
    return {
        'is_principle_admin': request.session.get('principle_admin_authenticated', False),
        'is_school_admin': request.session.get('school_admin_authenticated', False),
        'admin_type': 'Principle Admin' if request.session.get('principle_admin_authenticated') else 'School Admin'
    }
