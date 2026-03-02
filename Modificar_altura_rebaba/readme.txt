Altura.py
Entrada: Datos_Totales_Corregidos
Salida: Altura_Rebaba_Individual_Por_Ranura
Extrae los datos de Datos_Totales_Corregidos y genera la salida Datos totales corregidos es el archivo genérico original donde se agrupan todos los datos puros ordenados (por si cambia el nombre en un futuro) La fila general del archivo de datos puros ordenados actualmente es la siguiente por si cambia en un futuro (con esta funciona)
"FUENTE BASE	Potencia	Frecuencia	Velocidad	Ancho de Pulso	Densidad de energía	solapamiento	l [m]	z [m]	Unnamed: 7	FUENTE LINE	Potencia.1	Frecuencia.1	Velocidad.1	Ancho de Pulso.1	Densidad de energía.1	solapamiento.1	ID	Angle	Length	P1 X	P1 Y	P2 X	P2 Y	Slope	X-Int	Y-Int	Dev Mean	Dev Min	Dev Max	a	b	c	Unnamed: 29	FUENTE ANGLE	Potencia.2	Frecuencia.2	Velocidad.2	Ancho de Pulso.2	Densidad de energía.2	solapamiento.2	ID.1	Angle.1	Apex X	Apex Y	Unnamed: 39	FUENTE RUG. LINEA	Potencia.3	Frecuencia.3	Velocidad.3	Ancho de Pulso.3	Densidad de energía.3	solapamiento.3	Ra	Rq	Rt	Rz	Rmax	Rp	Rv	Rc	Rsm	Rsk	Rku	Rdq	Rt/Rz	l	Lc	Unnamed: 60	FUENTE SUP. TIPO 1	Potencia.4	Frecuencia.4	Velocidad.4	Ancho de Pulso.4	Densidad de energía.4	solapamiento.4	Sa	Sq	Sp	Sv	Sz	S10z	Ssk	Sku	Sdq	Sdr	FLTt	Lc.1	Unnamed: 78	FUENTE SUP. TIPO 2	Potencia.5	Frecuencia.5	Velocidad.5	Ancho de Pulso.5	Densidad de energía.5	solapamiento.5	Sk	Spk	Svk	Smr1	Smr2	Vmp	Vmc	Vvc	Vvv	Vvc/Vmc	Lc.2"


--------------------------------------------------------

modificar.py 
Entrada: Altura_Rebaba_Individual_Por_Ranura
Salida: Altura o Profundidad media por familia de las 81

Este flujo se hizo porque hubo un error en los datos provenientes de los archivos que estudiaban la geometría de las ranuras, había líneas mal hechas y hubo que enmendarlo de manera local ya que no era necesario cambiar el flujo general por un error que se podía enmendar de manera aislada. El error por si le interesa al lector, fue que al hacer las mediciones el programa no entendía entre izquierda o derecha en el estudio de la geometría que quiero decir, allí donde colocabas el primer punto era el punto 1 luego si por algún imprevisto se desordenaba el orden típico de colocación de puntos afectaba a la hora de calcular la profundidad o la altura de la rebaba ya que se hizo el cálculo en funciones la posición numérica aportada por el software de la Alicona.
