from datetime import datetime
from collections import deque

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Contact
from app.schemas import IdentifyRequest, ContactResponse, ContactPayload


def _get_primary_and_linked(db: Session, matches: list[Contact]) -> tuple[Contact, list[Contact]]:
    """Resolve primary (oldest root) and all linked contacts from matches."""
    primaries = [c for c in matches if c.linked_id is None]
    if not primaries:
        c = matches[0]
        while c and c.linked_id:
            parent = db.get(Contact, c.linked_id)
            if not parent or parent.deleted_at:
                break
            c = parent
        primary = c
    else:
        primary = min(primaries, key=lambda c: c.created_at)
    linked_ids = {primary.id}
    queue = deque([primary.id])
    while queue:
        pid = queue.popleft()
        secondaries = db.query(Contact).filter(
            Contact.linked_id == pid, Contact.deleted_at.is_(None)
        ).all()
        for s in secondaries:
            if s.id not in linked_ids:
                linked_ids.add(s.id)
                queue.append(s.id)
    linked = db.query(Contact).filter(Contact.id.in_(linked_ids)).order_by(Contact.created_at).all()
    return primary, linked


def identify(db: Session, request: IdentifyRequest) -> ContactResponse:
    email = request.email
    phone = str(request.phoneNumber) if request.phoneNumber else None

    conditions = []
    if email:
        conditions.append(Contact.email == email)
    if phone:
        conditions.append(Contact.phone_number == phone)

    matches = (
        db.query(Contact)
        .filter(Contact.deleted_at.is_(None))
        .filter(or_(*conditions))
        .all()
    )

    if not matches:
        contact = Contact(
            email=email,
            phone_number=phone,
            linked_id=None,
            link_precedence="primary",
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        emails = [e for e in [contact.email] if e]
        phones = [p for p in [contact.phone_number] if p]
        return ContactResponse(
            contact=ContactPayload(
                primaryContatctId=contact.id,
                emails=emails,
                phoneNumbers=phones,
                secondaryContactIds=[],
            )
        )

    primaries = [c for c in matches if c.linked_id is None]
    if len(primaries) >= 2:
        ordered = sorted(primaries, key=lambda c: c.created_at)
        oldest, to_demote = ordered[0], ordered[1:]
        for c in to_demote:
            c.linked_id = oldest.id
            c.link_precedence = "secondary"
            c.updated_at = datetime.utcnow()
        db.commit()
        matches = (
            db.query(Contact)
            .filter(Contact.deleted_at.is_(None))
            .filter(or_(*conditions))
            .all()
        )

    primary, linked = _get_primary_and_linked(db, matches)

    linked_emails = {c.email for c in linked if c.email}
    linked_phones = {c.phone_number for c in linked if c.phone_number}

    has_new_info = (email and email not in linked_emails) or (phone and phone not in linked_phones)
    if has_new_info:
        secondary = Contact(
            email=email,
            phone_number=phone,
            linked_id=primary.id,
            link_precedence="secondary",
        )
        db.add(secondary)
        db.commit()
        db.refresh(secondary)
        linked = linked + [secondary]

    emails_ordered = [primary.email] if primary.email else []
    for c in linked:
        if c.id != primary.id and c.email and c.email not in emails_ordered:
            emails_ordered.append(c.email)

    phones_ordered = [primary.phone_number] if primary.phone_number else []
    for c in linked:
        if c.id != primary.id and c.phone_number and c.phone_number not in phones_ordered:
            phones_ordered.append(c.phone_number)

    secondary_ids = [c.id for c in linked if c.id != primary.id]

    return ContactResponse(
        contact=ContactPayload(
            primaryContatctId=primary.id,
            emails=emails_ordered,
            phoneNumbers=phones_ordered,
            secondaryContactIds=secondary_ids,
        )
    )
