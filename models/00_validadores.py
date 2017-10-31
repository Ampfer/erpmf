# -*- coding: utf-8 -*-
# flavio@casacurta.com

import re

class IS_DECIMAL(IS_DECIMAL_IN_RANGE):

    def __call__(self, value):

        comma = ',' if self.dot == '.' else '.'
        import decimal
        try:
            if isinstance(value, decimal.Decimal):
                v = value
            else:
                v = decimal.Decimal(str(value).replace(comma,'').replace(self.dot, '.'))
            if self.minimum is None:
                if self.maximum is None or v <= self.maximum:
                    return (v, None)
            elif self.maximum is None:
                if v >= self.minimum:
                    return (v, None)
            elif self.minimum <= v <= self.maximum:
                    return (v, None)
        except (ValueError, TypeError, decimal.InvalidOperation):
            pass
        return (value, self.error_message)


class IS_MONEY(object):

    """
    Checks if field's value is a valid decimal money
    Examples::
        INPUT(_type='text', _name='name', requires=IS_MONEY())
        >>> IS_MONEY(0, 999.99, dot=',', symbol='R$')('R$ 123,45')
        (Decimal('123.45'), None)
        >>> IS_MONEY()('$ 123.45')
        (Decimal('123.45'), None)
    """

    def __init__(self, minimum=None
                     , maximum=None
                     , error_message=None
                     , dot=''
                     , symbol=''):

        self.minimum = minimum
        self.maximum = maximum
        self.error_message=error_message

        import locale
        locale.setlocale(locale.LC_ALL, "")
        if not dot:
            self.dot = locale.localeconv()['decimal_point']
        else:
            self.dot = dot
        if not symbol:
            self.symbol = locale.localeconv()['currency_symbol']
        else:
            self.symbol = symbol

    def __call__(self, money):

        value = str(money).replace(self.symbol, '').strip()
        return IS_DECIMAL(minimum=self.minimum
                         ,maximum=self.maximum
                         ,error_message=self.error_message
                         ,dot=self.dot)(value)


class IS_CPF(object):

    """
    Checks if field's value is a valid code CPF
    Examples::
        INPUT(_type='text', _name='name', requires=IS_CPF())
        >>> IS_CPF()('12345678900')
        ('12345678900', 'CPF Invalido')
        >>> IS_CPF()('123.456.789.09')
        ('123.456.789.09', 'CPF deve estar no formato 999.999.999-99')
        >>> IS_CPF()('12345678909')
        ('12345678909', None)
        >>> IS_CPF()('123456797')
        ('00123456797', None)
        >>> IS_CPF(mask=True)('123456797')
        ('001.234.567-97', None)
    """

    def __init__(self, error_message='CPF Invalido', mask = False):

        self.error_message = error_message
        self.mask = mask

    def __call__(self, cpf):

        digit_cpf = cpf
        if not cpf.isdigit():
            if not re.match(r'\d{3}(\.\d{3}){2}-\d{2}', cpf):
                return (cpf, 'CPF deve estar no formato 999.999.999-99')
            else:
                digit_cpf = UNMASK(str(cpf))

        if len(digit_cpf) > 11:
            return (cpf, 'CPF deve ter 11 digitos')

        safe_cpf = map(int, '0' * (11 - len(digit_cpf)) + digit_cpf)
        calc_cpf = safe_cpf[:9]

        while len(calc_cpf) < 11:
            r = sum(map(lambda(i,v):(len(calc_cpf)+1-i)*v,enumerate(calc_cpf))) % 11
            f = 11 - r if r > 1 else 0
            calc_cpf.append(f)

        if calc_cpf == safe_cpf:
            if self.mask:
                return (MASK_CPF()(safe_cpf), None)
            else:
                return (''.join(map(str, safe_cpf)), None)
        return (cpf, self.error_message)


class IS_CNPJ(object):
    """
    Checks if field's value is a valid code CNPJ
    Examples::
        INPUT(_type='text', _name='name', requires=IS_CNPJ())
        >>> IS_CNPJ()('123456000147')
        ('123456000147', 'CNPJ Invalido')
        >>> IS_CNPJ()('00.123.456/000149')
        ('00.123.456/000149', 'CNPJ deve estar no formato 99.999.999/9999-99')
        >>> IS_CNPJ()('00.123.456/0001-49')
        ('00123456000149', None)
        >>> IS_CNPJ()('123456000149')
        ('00123456000149', None)
        >>> IS_CNPJ(mask=True)('123456000149')
        ('00.123.456/0001-49', None)
    """
    def __init__(self, error_message='CNPJ Invalido', mask = False):

        self.error_message = error_message
        self.mask = mask

    def __call__(self, cnpj):

        digit_cnpj = cnpj
        if not cnpj.isdigit():
            if not re.match(r'\d{2}(\.\d{3}){2}/\d{4}-\d{2}', cnpj):
                return (cnpj, 'CNPJ deve estar no formato 99.999.999/9999-99')
            else:
                digit_cnpj = UNMASK(str(cnpj))

        if len(digit_cnpj) > 14:
            return (cnpj, 'CNPJ deve ter 14 digitos')

        safe_cnpj = map(int, '0' * (14 - len(digit_cnpj)) + digit_cnpj)
        calc_cnpj = safe_cnpj[:12]
        prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        while len(calc_cnpj) < 14:
            r = sum([x*y for (x, y) in zip(calc_cnpj, prod)])%11
            f = 11 - r if r > 1 else 0
            calc_cnpj.append(f)
            prod.insert(0, 6)

        if calc_cnpj == safe_cnpj:
            if self.mask:
                return (MASK_CNPJ()(safe_cnpj), None)
            else:
                return (''.join(map(str, safe_cnpj)), None)
        return (cnpj, self.error_message)


class IS_MODULO_10 (object):
    """
    Checks if field's value is a valid digit checker
    Examples::
        INPUT(_type='text', _name='name', requires=IS_MODULO_10())
        >>> IS_MODULO_10()('123456000147')
        ('123456000147', 'Digito Verificador Invalido')
        >>> IS_MODULO_10(mask='-')('00.12345600014-9')
        ('00.12345600014-9', 'Valor informado deve estar no formato 9(n)-9')
    """
    def __init__(self, error_message='Digito Verificador Invalido', mask = ''):

        self.error_message = error_message
        self.mask = mask

    def __call__(self, value):

        digit_value = value
        if not value.isdigit():
            if self.mask in ('-/'):
               if not re.match(r'\d{1,30}[-/]\d{1}', value):
                   return (value, 'Valor informado deve estar no formato 9(n){}9'.format(self.mask))
               else:
                   digit_value = UNMASK(str(value))
            else:
                return (value, 'Mask invalido')

        if len(digit_value) > 30:
            return (value, 'Valor informado deve ter no maximo 30 digitos')

        safe_value = map(int, digit_value)
        dv = safe_value[-1]
        v1 = safe_value[-3::-2]
        v2 = safe_value[-2::-2]
        s = sum(v1)
        for n in xrange(len(v2)):
            s += sum(map(int, (i for i in str(v2[n] * 2))))
        r = s % 10
        dvc = 10 - r if r else r

        if dvc == dv:
            return (digit_value, None)
        return (value, self.error_message)


class IS_MODULO_11(object):

    """
    Checks if field's value is a valid digit checker
    Examples::
        INPUT(_type='text', _name='name', requires=IS_MODULO_11())
        >>> IS_MODULO_11()('12345678900')
        ('12345678900', 'Digito Verificador Invalido')
        >>> IS_MODULO_11()('1.234.567.890-9')
        ('1.234.567.890-9', 'Valor informado deve estar no formato 9(n)-9')
        >>> IS_MODULO_11()('12345678909')
        ('12345678909', None)
        >>> IS_MODULO_11(mask='-')('123456797')
        ('12345679-7', None)
    """

    def __init__(self, error_message='Digito Verificador Invalido', mask = ''):

        self.error_message = error_message
        self.mask = mask

    def __call__(self, value):

        digit_value = value
        if not value.isdigit():
            if self.mask in ('-/'):
               if not re.match(r'\d{1,30}[-/]\d{1}', value):
                   return (value, 'Valor informado deve estar no formato 9(n){}9'.format(self.mask))
               else:
                   digit_value = UNMASK(str(value))
            else:
                return (value, 'Mask invalido')

        safe_value = map(int, digit_value)
        dv = safe_value[-1]
        calc_value = safe_value[:-1]

        r = sum(map(lambda(i,v):(len(calc_value)+1-i)*v,enumerate(calc_value))) % 11
        dvc = 11 - r if r > 1 else 0

        if dvc == dv:
            return (''.join(map(str, safe_value)), None)
        return (value, self.error_message)