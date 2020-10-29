$(document).ready(function(){
     //Aplicando as mascaras nos inputs cpf, valor e vencimento.
     $('#cpf').mask('000.000.000-00', {reverse: true});
     $('#valor').mask('000.000.000.000.000,00', {reverse: true});
     $('#vencimento').mask('0000-00-00');
     $('#telefone').mask('00 00000-0000', {reverse: true});
})