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

    def peek(self, step = 0):
        if self.pos + step >= len(self.prog):
            return 'eof'
        return self.prog[self.pos + step]
    
    def next(self):
        temp = self.cur
        self.pos = self.pos + 1
        if self.pos >= len(self.prog):
            self.cur = 'eof'
        else:
            self.cur = self.prog[self.pos]
        return temp

    def match(self, *m):
        if type(self.cur) == Token:
            if self.cur.Get_tag() not in m:
                error('match异常',f'应为{m}，实为{self.cur.Get_tag()}')
        else:
            if self.cur not in m:
                error('match异常',f'应为{m}，实为{self.cur}')
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
        
        
    def statement(self):
        if self.iterator.peek().Get_tag() == 'return':
            self.iterator.match('return')
            if self.iterator.peek().Get_tag() != ';':
                e = self.expr()
            else:
                e = None
            self.iterator.match(';')
            return ['return',e]
        
        if self.iterator.peek().Get_tag() == 'if':
            self.iterator.match('if')
            self.iterator.match('(')
            cond = self.expr()
            self.iterator.match(')')
            true_s = self.statement()
            if self.iterator.peek().Get_tag() == 'else':
                self.iterator.match('else')
                false_s = self.statement()
            else:
                false_s = None
            return ['if', cond, true_s, false_s]
        
        if self.iterator.peek().Get_tag() == 'while':
            self.iterator.match('while')
            self.iterator.match('(')
            cond = self.expr()
            self.iterator.match(')')
            while_body = self.statement()
            return ['while', cond, while_body]
        
        if self.iterator.peek().Get_tag() in ['break', 'continure']:
            bOrc = self.iterator.next().Get_tag()
            self.iterator.match(';')
            return[bOrc]
        
        if self.iterator.peek().Get_tag() == '{':
            self.iterator.match('{')
            brace_body = []
            while self.iterator.peek().Get_tag() != '}':
                brace_body.append(self.statement())
            self.iterator.match('}')
            return ['block', brace_body]
        
        if  self.iterator.peek().Get_tag() == 'fun':
            self.iterator.match('fun')
            tep = self.iterator.next()
            id = tep.Get_val()
            self.iterator.match('(')
            params = []
            if self.iterator.peek().Get_tag() != ')':
                params.append(self.iterator.match('id'))
                while self.iterator.peek().Get_tag() == ',':
                    self.iterator.match(',')
                    params.append(self.iterator.match('id'))
            self.iterator.match(')')
            if self.iterator.peek().Get_tag() != '{':
                fun_body = self.expr()
                self.iterator.match(';')
            else:
                self.iterator.match('{')
                fun_statements = []
                while self.iterator.peek().Get_tag() != '}':
                    fun_statements.append(self.statement())
                self.iterator.match('}')
                fun_body = ['block', fun_statements]
            return ['fun', id, params, fun_body]
        
        if self.iterator.peek().Get_tag() == 'print':
            self.iterator.match('print')
            self.iterator.match('(',None)
            args = []
            if self.iterator.peek().Get_tag() != ')':
                args.append(self.expr())
                while self.iterator.peek().Get_tag() == ',':
                    self.iterator.match(',')
                    args.append(self.expr())
            self.iterator.match(')')
            self.iterator.match(';')
            return ['print', args]
        
        if self.iterator.peek().Get_tag() == 'var':
            self.iterator.match('var')
            tep = self.iterator.match('id')
            id = tep.Get_val()
            if self.iterator.peek().Get_tag() == '=':
                self.iterator.match('=')
                expr = self.expr()
            self.iterator.match(';')
            return ['var', id, expr]
    
        if self.iterator.peek().Get_tag() == 'id' and self.iterator.peek(1).Get_tag() == '=':
            tep = self.iterator.next()
            id = tep.Get_val()
            self.iterator.match('=')
            expr = self.expr()
            self.iterator.match(';')
            return ['assign', id, expr]
        
        e = self.expr()
        self.iterator.match(';')
        return ['expr', e]
    
    def program(self):
        self.iterator.next()
        while self.iterator.peek().Get_tag() != 'eof':
            self.ast.append(self.statement())
        return ['program', self.ast]
    
    def expr(self):
        return self.logic_or()
    
    def logic_or(self):
        left = self.logic_and()
        while self.iterator.peek().Get_tag() == 'or':
            op = self.iterator.next()
            right = self.logic_and()
            left = ('binop','or',left,right)
        return left
    
    def logic_and(self):
        left = self.equality()
        while self.iterator.peek().Get_tag() == 'and':
            op = self.iterator.next()
            right = self.equality()
            left = ['binop','and',left,right]
        return left
    
    def equality(self):
        left = self.comparison()
        while self.iterator.peek().Get_tag() in ['==','!=']:
            op = self.iterator.next()
            right = self.comparison()
            left = ['binop',op.Get_tag(),left,right]
        return left
    
    def comparison(self):
        left = self.term()
        while self.iterator.peek().Get_tag() in ['>','<','>=','<=']:
            op = self.iterator.next()
            right = self.term()
            left = ['binop',op.Get_tag(),left,right]
        return left
    
    def term(self):
        left = self.factor()
        while self.iterator.peek().Get_tag() in ['+','-']:
            op = self.iterator.next()
            right = self.factor()
            left = ['binop',op.Get_tag(),left,right]
        return left
    
    def factor(self):
        left = self.unary()
        while self.iterator.peek().Get_tag() in ['*','/']:
            op = self.iterator.next()
            right = self.unary()
            left = ['binop',op.Get_tag(),left,right]
        return left

    def unary(self):
        ops = []
        while self.iterator.peek().Get_tag() in ['-','!']:
            ops.append(self.iterator.next().Get_tag())
        right = self.pow()
        ops.reverse()
        for op in ops:
            right = ['unary',op,right]
        return right
    
    def pow(self):
        left = self.atom()
        while self.iterator.peek().Get_tag() == '**':
            op = self.iterator.next().Get_tag()
            right = self.pow()
            left = ['binop',op,left,right]
        return left
    
    def atom(self):
        t = self.iterator.peek().Get_tag()
        if t in ['num','str','true','false','null']:
            tep = self.iterator.next()
            return [tep.Get_tag(),tep.Get_val()]
        elif t=='id':
            temp = self.iterator.next()
            if self.iterator.peek().Get_tag() != '(':
                id = [temp.Get_tag(),temp.Get_val()]
                return id
            else:
                id = temp.Get_val()
                self.iterator.match('(')
                args = []
                if self.iterator.peek().Get_tag() != ')':
                    args.append(self.expr())
                    while self.iterator.peek().Get_tag() == ',':
                        self.iterator.match(',')
                        args.append(self.expr())
                self.iterator.match(')')
                return ['call',id,args]
        elif t == '(':
            self.iterator.match('(')
            e = self.expr()
            self.iterator.match(')')
            return e
        return ['null',None]        
        

class Translator:
    @staticmethod
    def c2p(n):
        return n[1]
    @staticmethod
    def p2c(n):
        if type(n) == int or type(n) == float:
            return ['num',n]
        if type(n) == str:
            return ['str',n]
        if type(n) == bool:
            if n:
                return ['boolean',True]
            else:
                return ['boolean',False]
        if n == None:
            return ['null',None]

class Evaluator:
    def __init__(self, Ast, Env):
        self.ast = Ast
        self.env = Env 
        
    def eval_print(self,node,env):
        _, args = node
        for a in args:
            print(self.visit(a,env)[1],sep='' ,end='')
        return Translator.p2c(None)
    
    def eval_if(self,node,env):
        _, cond, ts, fs = node
        if self.visit(cond,env) == Translator.p2c(True):
            return self.visit(ts,env)
        if fs != None:
            return self.visit(fs,env)
        return Translator.p2c(None)
    
    def eval_while(self,node,env):
        _, cond, while_body = node
        v = Translator.p2c(None)
        while True:
            if self.visit(cond,env) == Translator.p2c(False):
                break
            v = self.visit(while_body,env)
            if v[0] == 'continue':
                continue
            if v[0] == 'break':
                break
            if v[0] == 'return':
                break
        return v
    def eval_continue(self,node,env):
        return ['continue']
    def eval_break(self,node,env):
        return ['break']
    def eval_return(self,node,env):
        _, e = node
        if e == None:
            v = Translator.p2c(None)
        else:
            v = self.visit(e,env)
        return ['return',v]
    
    def eval_block(self,node,env):
        _, statements = node
        new_env = ({},env)
        v = Translator.p2c(None)
        for s in statements:
            k = s
            v = self.visit(s,new_env)
            if v[0] in ['return','break','continue']:
                return v
        return v
    
    def eval_expr(self,node,env):
        _,e = node
        return self.visit(e,env)
    
    def eval_literal(self,node,env):
        tag = node[0]
        if tag in ['num','str']:
            return node
        if tag == 'true':
            return Translator.p2c(True)
        if tag == 'false':
            return Translator.p2c(False)
        if tag == 'null':
            return Translator.p2c(None)
        error('eval_literal',f'未知的字面量{node}')
        
    def eval_binop(self,node,env):
        _,op,left,right = node
        left = self.visit(left,env)
        right = self.visit(right,env)
        if left[0] == 'num' and right[0] == 'num':
            if op == '+':
                return Translator.p2c(Translator.c2p(left) + Translator.c2p(right))
            if op == '-':
                return Translator.p2c(Translator.c2p(left) - Translator.c2p(right))
            if op == '*':
                return Translator.p2c(Translator.c2p(left) * Translator.c2p(right))
            if op == '/':
                return Translator.p2c(Translator.c2p(left) / Translator.c2p(right))
            if op == '>':
                return Translator.p2c(Translator.c2p(left) > Translator.c2p(right))
            if op == '<':
                return Translator.p2c(Translator.c2p(left) < Translator.c2p(right)) 
            if op == '>=':
                return Translator.p2c(Translator.c2p(left) >= Translator.c2p(right))
            if op == '<=':
                return Translator.p2c(Translator.c2p(left) <= Translator.c2p(right))
            if op == '==':
                return Translator.p2c(Translator.c2p(left) == Translator.c2p(right))
            if op == '!=':
                return Translator.p2c(Translator.c2p(left) != Translator.c2p(right))
            if op == '**':
                return Translator.p2c(Translator.c2p(left) ** Translator.c2p(right))
            error('eval_binop',f'非法运算{op}')
        if left[0] == 'str' and right[0] == 'str':
            if op == '+':
                return Translator.p2c(Translator.c2p(left) + Translator.c2p(right))
            if op == '==':
                return Translator.p2c(Translator.c2p(left) == Translator.c2p(right))
            if op == '!=':
                return Translator.p2c(Translator.c2p(left) != Translator.c2p(right))
            error('eval_binop',f'非法运算{op}')
        if left[0] == 'str' and right[0] == 'num':
            if op == '*':
                return Translator.p2c(Translator.c2p(left) * Translator.c2p(right))
            error('eval_binop',f'非法运算{op}')
        if left[0] == 'boolean' and right[0] == 'boolean':
            if op == 'or':
                return Translator.p2c(Translator.c2p(left) or Translator.c2p(right))
            if op == 'and':
                return Translator.p2c(Translator.c2p(left) and Translator.c2p(right))
            error('eval_binop',f'非法运算{op}')
            
        error('eval_binop',f'非法运算{left[1]}{op}{right[1]}') 
        
    def eval_uniop(self,node,env):
        _,op,right = node
        right = self.visit(right,env)
        if right[0] == 'num':
            if op == '-':
                return Translator.p2c(-Translator.c2p(right))
            error('eval_uniop',f'非法运算{op}')
        if right[0] == 'boolean':
            if op == '!':
                return Translator.p2c(not Translator.c2p(right))
            error('eval_uniop',f'非法运算{op}')
            
        error('eval_uniop',f'非法运算{op}{right[1]}')
        
    def def_var(self,id, val, env):
        inner_env,outer_env = env
        if id in inner_env:
            error('def_var',f'变量{id}已存在')
        inner_env[id] = val
        
    def lookup_id(self,id,env):
        while env:
            inner_env,env = env
            if id in inner_env:
                return inner_env[id]
        error('lookup_id',f'未知变量{id}')
        
    def set_val(self,id,val,env):
        while env:
            inner_env,env = env
            if id in inner_env:
                inner_env[id] = val
                return Translator.p2c(None)
        error('set_val',f'未知变量{id}')
        
    def eval_var(self,node,env):
        _,id,expr = node
        if expr == None:
            val = Translator.p2c(None)
        else:
            val = self.visit(expr,env)
        self.def_var(id,val,env)
        return val
    
    def eval_id(self,node,env):
        _,id = node
        return self.lookup_id(id,env)
    
    def eval_assign(self,node,env):
        _,id,expr = node
        val = self.visit(expr,env)
        self.set_val(id,val,env)
        return self.lookup_id(id,env)
    
    def eval_fun(self,node,env):
        _,id,params,fun_body = node
        self.def_var(id,Translator.p2c(None),env)
        self.set_val(id, ['proc',params,fun_body,env],env)
        return self.lookup_id(id,env)
    
    def eval_call(self,node,env):
        _,func,args = node
        proc = self.lookup_id(func,env)
        if proc[0] != 'proc':
            error('eval_call',f'{func}不是函数')
        _,params,body,saved_env = proc
        if len(params) != len(args):
            error('eval_call',f'参数数量不匹配')
        new_env = ({},saved_env)
        for i in range(0,len(params)):
                new_env[0][params[i].Get_val()]=self.visit(args[i],env)
        v = self.visit(body,new_env)
        return v[1] if v[0] == 'return' else Translator.p2c(None)
        
    visitors={
        "print":eval_print,
        "if":eval_if,
        "while":eval_while,
        "continue":eval_continue,
        "break":eval_break,
        "return":eval_return,
        "block":eval_block,
        "expr":eval_expr,
        "num":eval_literal,
        "str":eval_literal,
        "true":eval_literal,
        "false":eval_literal,
        "null":eval_literal,
        "binop":eval_binop,
        "uniop":eval_uniop,
        "var":eval_var,
        "id":eval_id,
        "assign":eval_assign,
        "fun":eval_fun,
        "call":eval_call,
    }
    
        
    def visit(self, node, env):
        def node_tag(node):
            return node[0]
        t = node_tag(node)
        if t not in self.visitors:
            error('visit异常',f'未知节点类型{t}')
        return self.visitors[t](self,node,env)
        
    def eval_prog(self):
        _, statements = self.ast
        v = Translator.p2c(None)
        for s in statements:
            v = self.visit(s, self.env)
        return v
       
    

p = '''

print("Hello cilly!\n");

'''

p1 = '''

fun lingxing(a)
{
    var n=a;
    var i=1;
    while (i <= n)
    {
        print(" " * (n-i) + "*" * (2*i-1));
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
lingxing(10);

'''

p2 = '''

fun sum1to100(n)
{
    var i=1;
    var sum=0;
    fun add(a,b)
    {
        return a+b;
    }

    while (i <= n)
    {
        sum=sum+i;
        i = add(i,1);
    }
    return sum;
}

print(sum1to100(100));
print("\n");

'''

p3 = '''

fun fib(n)
{
    if (n <= 1)
    {
        return n;
    }
    return fib(n-1)+fib(n-2);
}

print(fib(10));
print("\n");

'''

lexer = Lexer(p)
tokens = lexer.Tokens()
parser = Parser(tokens)
ast = parser.program()
evaluator = Evaluator(ast,({},None))
evaluator.eval_prog()
    

global_env=({},None)

cmd = input('>>>')

while True:
    if cmd == 'exit':
        break
    lexer = Lexer(cmd)
    tokens = lexer.Tokens()
    parser = Parser(tokens)
    ast = parser.program()
    evaluator = Evaluator(ast,global_env)
    result = evaluator.eval_prog()
    if result != Translator.p2c(None):
        print(result)
    cmd = input('>>>')
    

        
