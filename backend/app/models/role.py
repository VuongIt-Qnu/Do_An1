"""
Role Model
Defines user roles: ADMIN, OWNER, USER
"""
from ..extensions import db


class Role(db.Model):
    """User role for authorization"""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)  # ADMIN, OWNER, USER
    description = db.Column(db.Text)

    # Relationships
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


# Helper function to get or create default roles
def init_roles():
    """Initialize default roles if they don't exist"""
    from ..extensions import db

    roles_data = [
        {'name': 'ADMIN', 'description': 'Administrator - Full system access'},
        {'name': 'OWNER', 'description': 'Hotel Owner - Manage own hotel'},
        {'name': 'USER', 'description': 'Customer - Book rooms'},
    ]

    for role_data in roles_data:
        if not Role.query.filter_by(name=role_data['name']).first():
            role = Role(**role_data)
            db.session.add(role)

    db.session.commit()
