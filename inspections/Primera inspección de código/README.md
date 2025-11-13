La primera quality issue que fue determinada para corregir fue dentro de la sección de código de 'views.py', la cual correspondía a: Define a constant instead of duplicating literal 'Permisos insuficientes' 4 times.
Esta issue fue seleccionado ya que es un fallo trivial que se duplique el string, por lo que extraer el literal a una constante mejora la mantenibilidad y elimina este smell.

La segunda quality issue fue encontrada en 'EnsayoResultados.vue', la cual correspondía a: prefer old.replaceWith(newCanvas) over parent.replaceChild(newCanvas, old).
Se eligió esta ya que es una recomendación de estilo para que el código sea más legible y evite errores.
