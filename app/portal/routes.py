# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.portal import bp
from app.models import Artist, OnboardingTask, Event, BrandDeal


@bp.route('/')
@login_required
def index():
    if current_user.is_manager:
        return redirect(url_for('main.dashboard'))

    if not current_user.artist_id:
        flash('Conta sem assessorado vinculado.', 'error')
        return redirect(url_for('auth.logout'))

    artist = Artist.query.get_or_404(current_user.artist_id)
    tasks = OnboardingTask.query.filter_by(artist_id=artist.id).order_by(
        OnboardingTask.sort_order
    ).all()
    pending_tasks = [t for t in tasks if t.status != 'concluido'][:8]

    next_week = datetime.now() + timedelta(days=14)
    upcoming = Event.query.filter(
        Event.artist_id == artist.id,
        Event.start_datetime >= datetime.now(),
        Event.start_datetime <= next_week,
    ).order_by(Event.start_datetime).limit(5).all()

    open_deals = BrandDeal.query.filter(
        BrandDeal.artist_id == artist.id,
        BrandDeal.status.in_(['prospeccao', 'proposta', 'negociacao']),
    ).count()

    return render_template(
        'portal/index.html',
        artist=artist,
        pending_tasks=pending_tasks,
        upcoming_events=upcoming,
        open_deals=open_deals,
        tasks_total=len(tasks),
        tasks_done=sum(1 for t in tasks if t.status == 'concluido'),
    )
