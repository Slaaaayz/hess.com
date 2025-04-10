from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from app.models.database import db, Attack, Log, Attacker
from datetime import datetime, timedelta
import csv
import io

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    # Statistiques pour le dashboard
    total_attacks = Attack.query.count()
    recent_attacks = Attack.query.filter(
        Attack.timestamp >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    top_attackers = Attacker.query.order_by(
        Attacker.last_seen.desc()
    ).limit(5).all()
    
    return render_template('index.html',
                         total_attacks=total_attacks,
                         recent_attacks=recent_attacks,
                         top_attackers=top_attackers)

@bp.route('/attacks')
@login_required
def attacks():
    page = request.args.get('page', 1, type=int)
    attacks = Attack.query.order_by(
        Attack.timestamp.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('attacks.html', attacks=attacks)

@bp.route('/attackers')
@login_required
def attackers():
    page = request.args.get('page', 1, type=int)
    attackers = Attacker.query.order_by(
        Attacker.last_seen.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('attackers.html', attackers=attackers)

@bp.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(
        Log.timestamp.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('logs.html', logs=logs)

@bp.route('/api/stats')
@login_required
def stats():
    # Statistiques pour les graphiques
    attacks_by_type = db.session.query(
        Attack.attack_type,
        db.func.count(Attack.id)
    ).group_by(Attack.attack_type).all()
    
    attacks_by_hour = db.session.query(
        db.func.strftime('%H', Attack.timestamp),
        db.func.count(Attack.id)
    ).group_by(db.func.strftime('%H', Attack.timestamp)).all()
    
    return jsonify({
        'attacks_by_type': dict(attacks_by_type),
        'attacks_by_hour': dict(attacks_by_hour)
    })

@bp.route('/api/attacks/<int:attack_id>')
@login_required
def get_attack_details(attack_id):
    attack = Attack.query.get_or_404(attack_id)
    logs = Log.query.filter_by(attack_id=attack_id).order_by(Log.timestamp.desc()).all()
    
    return jsonify({
        'id': attack.id,
        'timestamp': attack.timestamp.isoformat(),
        'source_ip': attack.source_ip,
        'attack_type': attack.attack_type,
        'severity': attack.severity,
        'description': attack.description,
        'service': attack.service,
        'logs': [{
            'timestamp': log.timestamp.isoformat(),
            'level': log.level,
            'message': log.message,
            'source': log.source
        } for log in logs]
    })

@bp.route('/api/block-ip', methods=['POST'])
@login_required
def block_ip():
    data = request.get_json()
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'success': False, 'error': 'IP address is required'}), 400
    
    attacker = Attacker.query.filter_by(ip_address=ip).first()
    if not attacker:
        return jsonify({'success': False, 'error': 'Attacker not found'}), 404
    
    attacker.is_blocked = True
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/api/attacks/export')
@login_required
def export_attacks():
    attacks = Attack.query.order_by(Attack.timestamp.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(['ID', 'Date', 'IP Source', 'Type', 'Sévérité', 'Service', 'Description'])
    
    # Données
    for attack in attacks:
        writer.writerow([
            attack.id,
            attack.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            attack.source_ip,
            attack.attack_type,
            attack.severity,
            attack.service,
            attack.description
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attacks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    ) 