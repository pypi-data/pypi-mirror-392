def verificar_cif(cif: str) -> bool:
    cif = cif.upper().strip()
    if len(cif) != 9:
        return False
    letras_validas = "ABCDEFGHJKLMNPQRSUVW"
    if cif[0] not in letras_validas:
        return False
    digitos = cif[1:-1]
    if not digitos.isdigit():
        return False
    control = cif[-1]
    suma_pares = sum(int(d) for i, d in enumerate(digitos, start=1) if i % 2 == 0)
    suma_impares = 0
    for i, d in enumerate(digitos, start=1):
        if i % 2 != 0:
            doble = int(d) * 2
            suma_impares += (doble // 10) + (doble % 10)
    total = suma_pares + suma_impares
    resto = total % 10
    digito_control = (10 - resto) % 10
    letras_control = "JABCDEFGHI"
    control_esperado = letras_control[digito_control]
    if cif[0] in "PQRSNW":
        return control == control_esperado
    elif cif[0] in "ABEH":
        return control == str(digito_control)
    else:
        return control in (str(digito_control), control_esperado)
