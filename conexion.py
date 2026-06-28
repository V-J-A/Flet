from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    Date, Time, DateTime, SmallInteger, Enum, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ============================================================
# CONFIGURACIÓN DE CONEXIÓN A LA BASE DE DATOS
# Se usa el driver "mysqlconnector" de SQLAlchemy para conectarse
# a MySQL en localhost. El formato de la URL es:
#   dialect+driver://usuario:contraseña@host:puerto/nombre_bd
#
# Hay tres URLs comentadas porque cada integrante del equipo
# tiene una contraseña distinta en su instalación local de MySQL.
# Antes de correr la app, cada uno descomenta la suya.
# ============================================================
#DATABASE_URL = "mysql+mysqlconnector://root:joacoagon2009@localhost:3306/academia"
DATABASE_URL = "mysql+mysqlconnector://root:Alvlgeddl09*@localhost:3306/academia"
#DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/academia"

# create_engine crea el motor de conexión: el objeto que sabe cómo
# hablar con MySQL. echo=False silencia el log de SQL en consola;
# cambiarlo a True es útil para debuggear queries.
engine = create_engine(DATABASE_URL, echo=False)

# sessionmaker devuelve una *clase* (no una instancia).
# Cada vez que llamamos a SessionLocal() obtenemos una sesión nueva,
# que es la unidad de trabajo de SQLAlchemy: agrupa queries y los
# confirma o revierte juntos.
SessionLocal = sessionmaker(bind=engine)

# Base es la clase padre de todos los modelos ORM.
# SQLAlchemy la usa para registrar las tablas y sus columnas,
# y para poder generar el esquema con Base.metadata.create_all(engine).
Base = declarative_base()


# ============================================================
# MODELOS ORM
# Cada clase representa una tabla en la base de datos "academia".
# Los atributos Column(...) mapean 1 a 1 con las columnas de la tabla.
# Los atributos relationship(...) son navegables en Python pero
# NO existen como columnas en la BD: SQLAlchemy los resuelve
# haciendo JOINs internamente cuando se accede a ellos.
# ============================================================


class Especialidad(Base):
    """Tabla: especialidad
    Representa una carrera o especialidad ofrecida por la academia.
    Es el nivel más alto de la jerarquía: Especialidad → Curso → Grupo → Alumno.
    """
    __tablename__ = 'especialidad'

    id              = Column(Integer, primary_key=True, autoincrement=True)
    codigo          = Column(String(10))           # Ej: "INF", "ADM"
    nombre          = Column(String(255))          # Nombre completo de la especialidad
    num_asignaturas = Column(Integer)              # Cantidad total de materias
    titulo_oficial  = Column(String(255))          # Título que otorga al completarla

    # Relación 1 a muchos: una especialidad tiene varios cursos
    cursos = relationship("Curso", back_populates="especialidad")


class Curso(Base):
    """Tabla: curso
    Representa un año/nivel dentro de una especialidad.
    Ej: 1° año de Informática, 2° año de Administración.
    """
    __tablename__ = 'curso'

    id               = Column(Integer, primary_key=True, autoincrement=True)
    numero_curso     = Column(Integer)                              # 1, 2, 3...
    id_especialidad  = Column(Integer, ForeignKey('especialidad.id'))  # FK a especialidad

    # Navegación hacia la especialidad padre
    especialidad = relationship("Especialidad", back_populates="cursos")
    # Un curso tiene varias asignaturas y varios grupos
    asignaturas  = relationship("Asignatura", back_populates="curso")
    grupos       = relationship("Grupo", back_populates="curso")


class Asignatura(Base):
    """Tabla: asignatura
    Materia dictada dentro de un curso.
    El tipo diferencia entre materias obligatorias (TRONCAL) y optativas (ESPECIALIZADA).
    """
    __tablename__ = 'asignatura'

    id       = Column(Integer, primary_key=True, autoincrement=True)
    codigo   = Column(String(20))                          # Código corto, ej: "MAT1"
    nombre   = Column(String(255))
    tipo     = Column(Enum('TRONCAL', 'ESPECIALIZADA'))    # Solo acepta estos dos valores
    id_curso = Column(Integer, ForeignKey('curso.id'))

    curso = relationship("Curso", back_populates="asignaturas")


class Profesor(Base):
    """Tabla: profesor
    Personal docente del sistema. El campo tipo determina
    qué rol puede cumplir: tutor de un grupo, especialista en una materia, o ambos.
    No tiene relationships porque es referenciado por muchas otras tablas
    (Grupo, HojaActividad, RegistroAsistencia, Comite) y se prefiere
    consultar en la dirección contraria.
    """
    __tablename__ = 'profesor'

    id             = Column(Integer, primary_key=True, autoincrement=True)
    dni            = Column(String(20))
    nombre         = Column(String(255))
    apellidos      = Column(String(255))
    domicilio      = Column(String(255))
    nivel_estudios = Column(String(255))
    titulacion     = Column(String(255))
    tipo           = Column(Enum('TUTOR', 'ESPECIALISTA', 'AMBOS'))


class Grupo(Base):
    """Tabla: grupo
    División de alumnos dentro de un curso. El código es A, B o C.
    Cada grupo tiene asignado un tutor (FK a profesor).
    """
    __tablename__ = 'grupo'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    codigo      = Column(Enum('A', 'B', 'C'))              # Letra identificadora del grupo
    id_curso    = Column(Integer, ForeignKey('curso.id'))
    num_alumnos = Column(Integer)
    id_tutor    = Column(Integer, ForeignKey('profesor.id'))

    curso  = relationship("Curso", back_populates="grupos")
    # Relación al tutor del grupo (un solo profesor)
    tutor  = relationship("Profesor")


class ProfesorEspecialista(Base):
    """Tabla: profesor_especialista
    Tabla de unión (muchos a muchos) que registra qué profesor especialista
    dicta qué asignatura en qué grupo. Un especialista puede cubrir
    varias asignaturas en varios grupos.
    """
    __tablename__ = 'profesor_especialista'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    id_profesor   = Column(Integer, ForeignKey('profesor.id'))
    id_grupo      = Column(Integer, ForeignKey('grupo.id'))
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))


class Alumno(Base):
    """Tabla: alumno
    Estudiante matriculado. Puede estar asignado a un grupo o no
    (nullable=True permite que id_grupo sea NULL mientras no tenga grupo).
    """
    __tablename__ = 'alumno'

    id        = Column(Integer, primary_key=True, autoincrement=True)
    dni       = Column(String(20))
    nombre    = Column(String(255))
    apellidos = Column(String(255))
    id_grupo  = Column(Integer, ForeignKey('grupo.id'), nullable=True)  # Puede estar sin grupo


class HojaActividad(Base):
    """Tabla: hoja_actividad
    Registro de una sesión de clase: qué profesor, en qué grupo,
    en qué fecha y en qué franja horaria.
    Sirve como libro de clases digital.
    """
    __tablename__ = 'hoja_actividad'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    id_grupo    = Column(Integer, ForeignKey('grupo.id'))
    fecha       = Column(Date)                    # Día de la clase
    id_profesor = Column(Integer, ForeignKey('profesor.id'))
    hora_inicio = Column(Time)                    # Hora de inicio de la sesión
    hora_fin    = Column(Time)                    # Hora de fin de la sesión


class FichaIndividual(Base):
    """Tabla: ficha_individual
    Ficha mensual de un alumno. Agrupa los registros de asistencia
    de ese alumno en un mes/año determinado.
    Es el "encabezado" de los registros de asistencia.
    """
    __tablename__ = 'ficha_individual'

    id        = Column(Integer, primary_key=True, autoincrement=True)
    id_alumno = Column(Integer, ForeignKey('alumno.id'))
    mes       = Column(Integer)        # 1-12
    anio      = Column(SmallInteger)   # Ej: 2024 (SmallInteger ahorra espacio para años)


class RegistroAsistencia(Base):
    """Tabla: registro_asistencia
    Una fila por cada día que un alumno asistió (o faltó) a una materia.
    Se vincula a la ficha mensual del alumno, a la asignatura y al profesor
    que tomó lista ese día.
    """
    __tablename__ = 'registro_asistencia'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    id_ficha      = Column(Integer, ForeignKey('ficha_individual.id'))
    dia           = Column(Integer)                              # Día del mes (1-31)
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))
    id_profesor   = Column(Integer, ForeignKey('profesor.id'))


class Candidato(Base):
    """Tabla: candidato
    Persona externa que postula para cubrir un puesto docente.
    El flujo de selección sigue la cadena:
        Candidato → Llamada → Entrevista → (contratación como Profesor)
    """
    __tablename__ = 'candidato'

    id           = Column(Integer, primary_key=True, autoincrement=True)
    dni          = Column(String(20))
    nombre       = Column(String(255))
    apellidos    = Column(String(255))
    curriculum   = Column(Text)                                    # Text permite textos largos
    tipo_deseado = Column(Enum('TUTOR', 'ESPECIALISTA', 'AMBOS')) # Rol al que aspira

    # Relaciones que permiten navegar al historial completo del candidato
    materias    = relationship("CandidatoMateria", back_populates="candidato")
    llamadas    = relationship("Llamada",          back_populates="candidato")
    entrevistas = relationship("Entrevista",       back_populates="candidato")


class CandidatoMateria(Base):
    """Tabla: candidato_materia
    Tabla de unión que registra qué asignaturas puede dictar un candidato.
    Un candidato puede tener competencia en varias materias.
    """
    __tablename__ = 'candidato_materia'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    id_candidato  = Column(Integer, ForeignKey('candidato.id'))
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))

    candidato = relationship("Candidato", back_populates="materias")


class Llamada(Base):
    """Tabla: llamada
    Registro de un intento de contacto con un candidato.
    La disposicion indica el resultado:
    - NO_LOCALIZADO: no atendió o no se pudo contactar
    - NO_INTERESADO: rechazó la oferta
    - ENTREVISTA_CONCERTADA: acordó una entrevista (siguiente paso)
    """
    __tablename__ = 'llamada'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    id_candidato= Column(Integer, ForeignKey('candidato.id'))
    fecha_hora  = Column(DateTime)   # Fecha y hora exacta de la llamada
    disposicion = Column(Enum('NO_LOCALIZADO', 'NO_INTERESADO', 'ENTREVISTA_CONCERTADA'))

    candidato = relationship("Candidato", back_populates="llamadas")


class Entrevista(Base):
    """Tabla: entrevista
    Entrevista presencial con un candidato, originada a partir de una llamada
    con disposicion='ENTREVISTA_CONCERTADA'. La valoracion es el juicio
    del comité tras la entrevista.
    """
    __tablename__ = 'entrevista'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    id_candidato  = Column(Integer, ForeignKey('candidato.id'))
    id_llamada    = Column(Integer, ForeignKey('llamada.id'))     # Llamada que la originó
    fecha         = Column(Date)
    id_asignatura = Column(Integer, ForeignKey('asignatura.id')) # Materia para la que se evalúa
    valoracion    = Column(String(255))                          # Texto libre con la evaluación
    id_comite     = Column(Integer, ForeignKey('comite.id'))     # Comité que realizó la entrevista

    candidato = relationship("Candidato", back_populates="entrevistas")


class Comite(Base):
    """Tabla: comite
    Comité selectivo anual encargado de evaluar a los candidatos.
    Está compuesto por tres profesores: presidente, secretario y vocal.
    Las tres FKs apuntan a la misma tabla (profesor), por eso SQLAlchemy
    no infiere la relación automáticamente y se usan IDs directamente.
    """
    __tablename__ = 'comite'

    id             = Column(Integer, primary_key=True, autoincrement=True)
    anio           = Column(SmallInteger)                          # Año del comité, ej: 2024
    id_presidente  = Column(Integer, ForeignKey('profesor.id'))
    id_secretario  = Column(Integer, ForeignKey('profesor.id'))
    id_vocal       = Column(Integer, ForeignKey('profesor.id'))


# ============================================================
# FUNCIÓN DE SESIÓN (estilo FastAPI / dependencias)
# get_db() es un patrón alternativo a llamar SessionLocal() directamente.
# Abre la sesión, la devuelve y la cierra en el bloque finally,
# garantizando que siempre se libere aunque ocurra una excepción.
#
# NOTA: en la app actual (main.py) se prefiere usar SessionLocal()
# directamente y cerrar manualmente. Esta función está disponible
# para usarla como dependencia si se migra a FastAPI en el futuro.
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()