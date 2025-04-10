from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import relationship
from flask_login import UserMixin

db = SQLAlchemy()

def convert_datetime_to_str(obj):
    """Convertit les objets datetime en chaînes de caractères pour la sérialisation JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

class Attack(db.Model):
    __tablename__ = 'attacks'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source_ip = db.Column(db.String(45), nullable=False)
    attack_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    service = db.Column(db.String(20), nullable=False)
    
    # Relations
    logs = relationship("Log", back_populates="attack")
    attacker_id = db.Column(db.Integer, db.ForeignKey('attackers.id'))
    attacker = relationship("Attacker", back_populates="attacks")

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50), nullable=False)
    
    # Relations
    attack_id = db.Column(db.Integer, db.ForeignKey('attacks.id'))
    attack = relationship("Attack", back_populates="logs")

class Attacker(db.Model):
    __tablename__ = 'attackers'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    country = db.Column(db.String(50))
    is_blocked = db.Column(db.Boolean, default=False)
    
    # Relations
    attacks = relationship("Attack", back_populates="attacker")

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Relations
    audits = relationship("Audit", back_populates="user")

class Audit(db.Model):
    __tablename__ = 'audits'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    
    # Relations
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship("User", back_populates="audits")

# Fonction pour enregistrer les audits
@event.listens_for(db.session, 'after_flush')
def receive_after_flush(session, context):
    for instance in session.new:
        if isinstance(instance, (Attack, Log, Attacker, User)):
            # Convertir les objets datetime en chaînes de caractères
            new_values = {k: convert_datetime_to_str(v) for k, v in instance.__dict__.items() if not k.startswith('_')}
            audit = Audit(
                action='CREATE',
                table_name=instance.__tablename__,
                record_id=instance.id,
                new_values=new_values
            )
            session.add(audit)
    
    for instance in session.dirty:
        if isinstance(instance, (Attack, Log, Attacker, User)):
            # Convertir les objets datetime en chaînes de caractères
            old_values = {k: convert_datetime_to_str(getattr(instance, k)) for k in instance.__dict__.keys() if not k.startswith('_')}
            new_values = {k: convert_datetime_to_str(v) for k, v in instance.__dict__.items() if not k.startswith('_')}
            audit = Audit(
                action='UPDATE',
                table_name=instance.__tablename__,
                record_id=instance.id,
                old_values=old_values,
                new_values=new_values
            )
            session.add(audit)
    
    for instance in session.deleted:
        if isinstance(instance, (Attack, Log, Attacker, User)):
            # Convertir les objets datetime en chaînes de caractères
            old_values = {k: convert_datetime_to_str(v) for k, v in instance.__dict__.items() if not k.startswith('_')}
            audit = Audit(
                action='DELETE',
                table_name=instance.__tablename__,
                record_id=instance.id,
                old_values=old_values
            )
            session.add(audit) 