keywords = ['fun','return',
            'print','input',
            'if','else','while','break','continue',
            'var','or','and','true','false','not','null']
def isdigit(m):
    return m >= '0' and m <= '9'
def isletter_(m):
    return m == '_' or (m >= 'a' and m <= 'z') or (m >= 'A' and m <= 'Z')

def error(src,msg):
    raise Exception(f'<{src}>,{msg}')

class Token:
    def __init__(self, Type, Val = None):
        if Val == 0:
            self.type = Type
            self.val = Val
        else:
            if Val:
                self.type = Type
                self.val = Val
            else:
                self.type = Type
                self.val = None
    def Get_tag(self):
        return self.type
    def Get_val(self):
        return self.val
        

class Iterator:
    def __init__(self, Prog):
        self.pos = -1
        self.cur = None
        self.prog = Prog

    def peek(self):
        return self.cur
    
    def next(self):
        temp = self.cur
        self.pos = self.pos + 1
        if self.pos >= len(self.prog):
            self.cur = 'eof'
        else:
            self.cur = self.prog[self.pos]
        return temp

    def match(self, m):
        if self.cur != m:
            error('match异常',f'期望是{m},实际上是{self.cur}')
        return self.next()


class Lexer:

    def __init__(self, Prog):
        self.tokens = []
        self.iterator = Iterator(Prog)
    def skip(self):
        while self.iterator.peek() in [' ', '\t', '\v', '\r', '\n']:
            self.iterator.next()
    def strToken(self):
        self.iterator.match('\"')
        r = ""
        while self.iterator.peek() != '\"':
            r = r + self.iterator.next()
        self.iterator.match('\"')
        return Token('str',r)
    def numToken(self):
        r = self.iterator.next()
        while isdigit(self.iterator.peek()):
            r = r + self.iterator.next()
        if self.iterator.peek() == '.':
            r = r + self.iterator.next()
            while isdigit(self.iterator.next()):
                r = r + self.iterator.next()
        return Token('num',float(r) if '.' in r else int(r))
    def idOrkeyword_Token(self):
        r = self.iterator.next()
        while isletter_(self.iterator.peek()) or isdigit(self.iterator.peek()):
            r = r + self.iterator.next()
        if r in keywords:
            return Token(r,None)
        else:
            return Token('id',r)
    def Get_Token(self):
        self.skip()
        m = self.iterator.peek()
        if m == 'eof':
            return Token('eof',None)
        if m in ['+', '-', '/', ';', ',', '(', ')','{','}']:
            self.iterator.next()
            return Token(m,None)
        if m == '*':
            self.iterator.next()
            if self.iterator.peek() == '*':
                self.iterator.next()
                return Token('**',None)
            else:
                return Token('*', None)
        if m == '=':
            self.iterator.next()
            if self.iterator.peek() == '=':
                self.iterator.next()
                return Token('==',None)
            else:
                return Token('=',None)
        if m == '!':
            self.iterator.next()
            if self.iterator.peek() == '=':
                self.iterator.next()
                return Token('!=', None)
            else:
                return Token('!',None)
        if m == '>':
            self.iterator.next()
            if self.iterator.peek() == '=':
                self.iterator.next()
                return Token('>=',None)
            else:
                return Token('>',None)
        if m == '<':
            self.iterator.next()
            if self.iterator.peek() == '=':
                self.iterator.next()
                return Token('<=',None)
            else:
                return Token('<',None)
        if m == '\"':
            return self.strToken()
        if isdigit(m):
            return self.numToken()
        if isletter_(m):
            return self.idOrkeyword_Token()
        error('Get_Token',f'非法字符{m}')
    def Tokens(self):
        self.iterator.next()
        while True:
            token = self.Get_Token()
            self.tokens.append(token)
            if token.Get_tag() == 'eof':
                break
        return self.tokens


class Parser:
    def __init__(self, Tokens):
        self.ast = []
        self.iterator = Iterator(Tokens)
    

    def expr(self):
        return logic_or()
    def logic_or(self):
        left = logic_and()
        while self.iterator.peek().Get_tag() == 'or':
            op = self.iterator.next()
            right = logic_and()
            left = ('binop','or',left,right)
        return left
    def logic_and(self):
        left = equality()
        while self.iterator.peek().Get_tag() == 'and':
            op = self.iterator.next()
            right = equality()
            left = ('binop','and',left,right)
        return left
    def equality(self):
        left = comparison()
        while self.iterator.peek().Get_tag() in ['==','!=']:
            op = self.iterator.next()
            right = comparison()
            left = ('binop',op.Get_tag(),left,right)
        return left
    def comparison(self):
        left term()
        while self.iterator.peek().Get_tag() in ['>','<','>=','<=']:
            op = self.iterator.next()
            right = term()
            left = ('binop',op.Get_tag(),left,right)
        return left
    def term(self):
        left = factor()
        while self.iterator.peek().Get_tag() in ['+','-']:
            op = self.iterator.next()
            right = factor()
            left = ('binop',op.Get_tag(),left,right)
        return left
    def factor(self):
        left = unary()
        while self.iterator.peek().Get_tag() in ['*','/']:
            op = self.iterator.next()
            right = unary()
            left = ('binop',op.Get_tag(),left,right)
        return left
    #一元运算符先peek()['-','!']
    def unary(self):
        if 

    

    

p = '''

fun diamond()
{
    var n=input("请输入菱形的大小:");
    var i=1;
    while (i <= n)
    {
        print(" "*(n-i)+"*"*(2*i-1));
        print("\n");
        i=i+1;
    }
    i=i-1;
    while (i>=0)
    {
        print(" "*(n-i)+"*"*(2*i-1));
        print("\n");
        i=i-1;
    }
}
diamond();

'''

lexer = Lexer(p)
tokens = lexer.Tokens()
for token in tokens:
    print([token.Get_tag(),token.Get_val()])
    

        
