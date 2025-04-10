from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.database import db, Attack, Log, Attacker
from datetime import datetime, timedelta

bp = Blueprint('api', __name__)

@bp.route('/attacks', methods=['GET'])
@login_required
def get_attacks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    attacks = Attack.query.order_by(
        Attack.timestamp.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'attacks': [{
            'id': attack.id,
            'timestamp': attack.timestamp.isoformat(),
            'source_ip': attack.source_ip,
            'attack_type': attack.attack_type,
            'severity': attack.severity,
            'description': attack.description,
            'service': attack.service
        } for attack in attacks.items],
        'total': attacks.total,
        'pages': attacks.pages,
        'current_page': attacks.page
    })

@bp.route('/attackers', methods=['GET'])
@login_required
def get_attackers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    attackers = Attacker.query.order_by(
        Attacker.last_seen.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'attackers': [{
            'id': attacker.id,
            'ip_address': attacker.ip_address,
            'first_seen': attacker.first_seen.isoformat(),
            'last_seen': attacker.last_seen.isoformat(),
            'country': attacker.country,
            'is_blocked': attacker.is_blocked,
            'attack_count': len(attacker.attacks)
        } for attacker in attackers.items],
        'total': attackers.total,
        'pages': attackers.pages,
        'current_page': attackers.page
    })

@bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs = Log.query.order_by(
        Log.timestamp.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'timestamp': log.timestamp.isoformat(),
            'level': log.level,
            'message': log.message,
            'source': log.source
        } for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    })

@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    # Statistiques globales
    total_attacks = Attack.query.count()
    total_attackers = Attacker.query.count()
    
    # Attaques des dernières 24h
    recent_attacks = Attack.query.filter(
        Attack.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    # Attaques par type
    attacks_by_type = db.session.query(
        Attack.attack_type,
        db.func.count(Attack.id)
    ).group_by(Attack.attack_type).all()
    
    # Attaques par heure
    attacks_by_hour = db.session.query(
        db.func.strftime('%H', Attack.timestamp),
        db.func.count(Attack.id)
    ).group_by(db.func.strftime('%H', Attack.timestamp)).all()
    
    return jsonify({
        'total_attacks': total_attacks,
        'total_attackers': total_attackers,
        'recent_attacks': recent_attacks,
        'attacks_by_type': dict(attacks_by_type),
        'attacks_by_hour': dict(attacks_by_hour)
    }) 