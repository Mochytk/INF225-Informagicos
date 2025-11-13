Para solucionar la issue hallada en 'views.py', se eliminaron literales repetidos del mensaje de permiso.
Ahora 'Permisos insuficientes' está definido una sola vez como constante 'PERMISO_DENEGADO' y todas las respuestas 403 la usan.
Esto con el objetivo de reducir duplicación y mejorar la mantenibilidad del código.

En cuanto a la segunda quality issue, en lugar de usar siempre 'parent.replaceChild(newCanvas, old)' ahora se usa 'old.replaceWith(newCanvas)'.
Aquello reduce la posibilidad de errores y soluciona el error detectado en SonarQube, sin cambiar la lógica de dibujo.
