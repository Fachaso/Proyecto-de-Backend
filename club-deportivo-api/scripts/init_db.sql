CREATE DATABASE IF NOT EXISTS club_deportivo;
USE club_deportivo;

CREATE TABLE IF NOT EXISTS deportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS canchas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_deporte INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    precio_hora INT NOT NULL,
    techada BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_deporte) REFERENCES deportes(id)
);

CREATE TABLE IF NOT EXISTS socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,
    tarifa_historica INT NOT NULL,
    total INT NOT NULL,
    estado ENUM('confirmada', 'cancelada', 'finalizada') DEFAULT 'confirmada',
    FOREIGN KEY (id_socio) REFERENCES socios(id),
    FOREIGN KEY (id_cancha) REFERENCES canchas(id)
);


INSERT IGNORE INTO deportes (nombre)
VALUES 
    ('Fútbol'), 
    ('Tenis'), 
    ('Pádel');


INSERT INTO canchas (id_deporte, nombre, precio_hora, techada, activa)
SELECT id, 'Cancha Fútbol 1', 1000000, FALSE, TRUE
FROM deportes WHERE nombre = 'Fútbol'
AND NOT EXISTS (SELECT 1 FROM canchas WHERE nombre = 'Cancha Fútbol 1');

INSERT INTO canchas (id_deporte, nombre, precio_hora, techada, activa)
SELECT id, 'Cancha Tenis 1', 800000, TRUE, TRUE
FROM deportes WHERE nombre = 'Tenis'
AND NOT EXISTS (SELECT 1 FROM canchas WHERE nombre = 'Cancha Tenis 1');

INSERT INTO canchas (id_deporte, nombre, precio_hora, techada, activa)
SELECT id, 'Cancha Pádel 1', 900000, TRUE, FALSE
FROM deportes WHERE nombre = 'Pádel'
AND NOT EXISTS (SELECT 1 FROM canchas WHERE nombre = 'Cancha Pádel 1');


INSERT IGNORE INTO socios (nombre, email, activo)
VALUES 
    ('Juan Pérez', 'juan.perez@example.com', TRUE),
    ('María Gómez', 'maria.gomez@example.com', TRUE),
    ('Pedro López', 'pedro.lopez@example.com', FALSE);


INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, tarifa_historica, total, estado)
SELECT s.id, c.id, '2026-10-15 18:00:00', '2026-10-15 20:00:00', c.precio_hora, c.precio_hora * 2, 'confirmada'
FROM socios s
JOIN canchas c ON c.nombre = 'Cancha Fútbol 1'
WHERE s.email = 'juan.perez@example.com'
AND NOT EXISTS (
    SELECT 1 FROM reservas r 
    WHERE r.id_socio = s.id AND r.id_cancha = c.id AND r.fecha_hora_inicio = '2026-10-15 18:00:00'
);


INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, tarifa_historica, total, estado)
SELECT s.id, c.id, '2026-10-16 19:00:00', '2026-10-16 20:00:00', c.precio_hora, c.precio_hora, 'finalizada'
FROM socios s
JOIN canchas c ON c.nombre = 'Cancha Tenis 1'
WHERE s.email = 'maria.gomez@example.com'
AND NOT EXISTS (
    SELECT 1 FROM reservas r 
    WHERE r.id_socio = s.id AND r.id_cancha = c.id AND r.fecha_hora_inicio = '2026-10-16 19:00:00'
);