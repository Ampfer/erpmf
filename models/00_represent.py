# -*- coding: utf-8 -*-
# flavio@casacurta.com

UNMASK = lambda num: re.sub('([^\d]+)', '', num or '')

class MASK_DECIMAL(object):
    """
    Edit the a value mask
    If "Decimal point is comma" was defined, comma separator is dot
    example::
        db.mytable.mycolumn.represent = lambda value, row: MASK_DECIMAL()(value, 0)
        >>> MASK_DECIMAL()('.12', 2)
        '0.12'
        >>> MASK_DECIMAL(dot=',')(',12', 2)
        '0,12'
        >>> MASK_DECIMAL()('12345.67', 3)
        '12,345.670'
        >>> MASK_DECIMAL(dot=',')('1234,567', 3)
        '1.234,567'
    """

    def __init__(self, dot='.'):
         self.dot = dot
         self.comma = ',' if dot == '.' else '.'


    def __call__(self, value, dec=0):
        value = str(value)
        id = IS_DECIMAL_IN_RANGE(dot=self.dot)(value)
        sign = ''
        if not id[1] and id[0] < 0:
            sign = '-'
            value = value[1:]
        if dec:
            pdot = value.find(self.dot) + 1
            z = dec - (len(value) - (pdot)) if pdot else dec
            value = value + ('0' * z)
        value = value.replace(".", "").replace(",", "")
        if len(value) == dec:
            value = '0' + value
        q_int = len(value)-dec
        r = q_int % 3
        mask = eval("'{}{}{}{}'.format('{}' * r if r else ''\
                                     ,self.comma if q_int > 3 and r else ''\
                                     ,(('{}{}{}' + self.comma) * (q_int/3))[:-1]\
                                     ,self.dot + '{}' * dec if dec else '')").format(*value)

        return sign + mask


class MASK_MONEY(object):
    """
    Edit the a value money mask
    example::
        db.mytable.mycolumn.represent = lambda value, row: MASK_MONEY(symbol='R$')(value, 0)
        >>> MASK_MONEY()('.12', 2)
        '$ 0.12'
        >>> MASK_MONEY(dot=',')(',12', 2)
        '$ 0,12'
        >>> MASK_MONEY()('12345.67', 3)
        '$ 12,345.670'
        >>> MASK_MONEY(dot=',', symbol='R$')('1234,567', 3)
        'R$ 1.234,567'
    """

    def __init__(self, dot='', symbol=''):
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

    def __call__(self, value, dec=0):
        rep =  ',' if self.dot == '.' else '.'
        value = str(value).replace(rep, self.dot).replace(self.symbol, '')
        return '{} {}'.format(self.symbol, MASK_DECIMAL(dot=self.dot)(value, dec))


class MASK_CPF(object):
    """
    Edit the a CPF code mask
    example::
        db.mytable.mycolumn.represent = lambda value, row: MASK_CPF()(value)
        >>> MASK_CPF()('12345678909')
        '123.456.789-09'
        >>> MASK_CPF()('123456797')
        '001.234.567-97'
    """
    def __init__(self):
        pass

    def __call__(self, cpf):
        if not isinstance(cpf,(list, str)):
           cpf=str(cpf)
        if isinstance(cpf, str):
           cpf = UNMASK(cpf)
           cpf = '0' * (11 - len(cpf)) + cpf
        return '{}{}{}.{}{}{}.{}{}{}-{}{}'.format(*cpf)


class MASK_CNPJ(object):
    """
    Edit the a CNPJ code mask
    example::
        db.mytable.mycolumn.represent = lambda value, row: MASK_CNPJ()(value)
        >>> MASK_CNPJ()('12345678000195')
        '12.345.678/0001-95'
        >>> MASK_CNPJ()('123456000149')
        '00.123.456/0001-49'
    """
    def __init__(self):
        pass

    def __call__(self, cnpj):
        if not isinstance(cnpj,(list, str)):
           cnpj=str(cnpj)
        if isinstance(cnpj, str):
           cnpj = UNMASK(cnpj)
           cnpj = '0' * (14 - len(cnpj)) + cnpj
        return '{}{}.{}{}{}.{}{}{}/{}{}{}{}-{}{}'.format(*cnpj)


class MASK_DV(object):
    """
    Edit the a digit checker
    example::
        db.mytable.mycolumn.represent = lambda value, row: MASK_DV('/')(value)
        >>> MASK_DV('-')('12345678000195')
        '1234567800019-5'
    """
    def __init__(self, mask=''):
        self.mask = mask

    def __call__(self, value):
        if not isinstance(value,(list, str)):
           value=str(value)
        if isinstance(value, str):
           value = UNMASK(value)
        return '{}{}{}'.format(value[:-1], self.mask, value[-1])