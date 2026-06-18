from sqlalchemy.orm import Session
from coneccion import SessionLocal, Profesor, ProfesorEspecialista, Grupo, Asignatura


def listar_profesores(db: Session):
    return db.query(Profesor).all()


def crear_profesor(db: Session, dni, nombre, apellidos, domicilio, nivel_estudios, titulacion, tipo):
    prof = Profesor(dni=dni, nombre=nombre, apellidos=apellidos, domicilio=domicilio,
                    nivel_estudios=nivel_estudios, titulacion=titulacion, tipo=tipo)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


def actualizar_profesor(db: Session, id_prof, dni=None, nombre=None, apellidos=None,
                        domicilio=None, nivel_estudios=None, titulacion=None, tipo=None):
    prof = db.query(Profesor).get(id_prof)
    if prof:
        if dni: prof.dni = dni
        if nombre: prof.nombre = nombre
        if apellidos: prof.apellidos = apellidos
        if domicilio: prof.domicilio = domicilio
        if nivel_estudios: prof.nivel_estudios = nivel_estudios
        if titulacion: prof.titulacion = titulacion
        if tipo: prof.tipo = tipo
        db.commit()
        db.refresh(prof)
    return prof


def eliminar_profesor(db: Session, id_prof):
    prof = db.query(Profesor).get(id_prof)
    if prof:
        db.delete(prof)
        db.commit()
    return prof


def asignar_especialista(db: Session, id_profesor, id_grupo, id_asignatura):
    esp = ProfesorEspecialista(id_profesor=id_profesor, id_grupo=id_grupo, id_asignatura=id_asignatura)
    db.add(esp)
    db.commit()
    db.refresh(esp)
    return esp


def listar_especialistas(db: Session):
    return db.query(ProfesorEspecialista).all()


def tutores_disponibles(db: Session):
    return db.query(Profesor).filter(Profesor.tipo.in_(['TUTOR', 'AMBOS'])).all()
