<?php
header("Content-Type: application/json; charset=utf-8");

if($_SERVER['REQUEST_METHOD']!== 'POST'){
    http_response_code(404);
    echo json_encode([
        'status' => 'error',
        'mensaje' => 'metodo no permitido'
    ]);
    exit;
}
$datosJson = file_get_contents('php://input');

$datos = json_decode($datosJson, true);

$nombre = $datos['nombre'] ?? '';
$apellido = $datos['apellido'] ?? '';
$cedula = $datos['cedula'] ?? '';

if(empty($nombre) || empty($apellido) || empty($cedula)){
    header('Content-Type : application/json');
    echo json_encode([
        'status' => 'error',
        'mensaje' => 'campos vacíos, verifique y reintente'
    ]);
    exit;

}

$pathPython = "/home/rasvuela/virtualenv/bot-user-register/3.9/bin/python";
$scriptUrl = "/home/rasvuela/bot-user-register/botUserRegister.py";

$cmd = sprintf(
    'HOME=/home/rasvuela%s %s %s %s %s 2>&1',
    $pathPython,
    escapeshellarg($scriptUrl),
    escapeshellarg($nombre),
    escapeshellarg($apellido),
    escapeshellarg($cedula)
);
$response = shell_exec($cmd);

echo $response;

?>