from sqlalchemy.orm import Session
from conexion import SessionLocal, Candidato, CandidatoMateria, Llamada, Entrevista, Asignatura, Comite


def listar_candidatos(db: Session):
    return db.query(Candidato).all()


def crear_candidato(db: Session, dni, nombre, apellidos, curriculum, tipo_deseado):
    c = Candidato(dni=dni, nombre=nombre, apellidos=apellidos,
                  curriculum=curriculum, tipo_deseado=tipo_deseado)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def actualizar_candidato(db: Session, id_c, dni=None, nombre=None, apellidos=None,
                         curriculum=None, tipo_deseado=None):
    c = db.query(Candidato).get(id_c)
    if c:
        if dni: c.dni = dni
        if nombre: c.nombre = nombre
        if apellidos: c.apellidos = apellidos
        if curriculum: c.curriculum = curriculum
        if tipo_deseado: c.tipo_deseado = tipo_deseado
        db.commit()
        db.refresh(c)
    return c


def eliminar_candidato(db: Session, id_c):
    c = db.query(Candidato).get(id_c)
    if c:
        db.delete(c)
        db.commit()
    return c


def agregar_materia_candidato(db: Session, id_candidato, id_asignatura):
    cm = CandidatoMateria(id_candidato=id_candidato, id_asignatura=id_asignatura)
    db.add(cm)
    db.commit()
    db.refresh(cm)
    return cm


def listar_llamadas(db: Session):
    return db.query(Llamada).all()


def crear_llamada(db: Session, id_candidato, fecha_hora, disposicion):
    ll = Llamada(id_candidato=id_candidato, fecha_hora=fecha_hora, disposicion=disposicion)
    db.add(ll)
    db.commit()
    db.refresh(ll)
    return ll


def listar_entrevistas(db: Session):
    return db.query(Entrevista).all()


def crear_entrevista(db: Session, id_candidato, id_llamada, fecha, id_asignatura, valoracion, id_comite):
    e = Entrevista(id_candidato=id_candidato, id_llamada=id_llamada, fecha=fecha,
                   id_asignatura=id_asignatura, valoracion=valoracion, id_comite=id_comite)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def listar_asignaturas(db: Session):
    return db.query(Asignatura).all()
