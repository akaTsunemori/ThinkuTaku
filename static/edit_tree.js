
document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-tree')
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Erro ao obter nome:', error);
        });
});

function closeAll(){
    $('#tree ul').fadeOut(600,function() {$(this).css('display', 'none')});
}

$(function(){
    $('#tree').on("click", ".quadro-t", function() {
        $( this ).siblings().toggle( "slow" );
    })
    $('#tree').on("click", ".action-button", function(event) {
        event.stopPropagation();
        $galho = $( this ).parent('.quadro-t').siblings('ul');
        if($( this ).hasClass('fa-plus-circle')){
            if($galho.length > 0){
                if($galho.css('display') == 'none'){
                    $galho.toggle("slow");
                }
                $novo = $galho.append("<li class='children' style='display: none'><div class='quadro-t "+"'><i class='far fa-trash-alt action-button'></i><i class='fas fa-plus-circle action-button'></i><input type='text' class='input-text' value='New'/></div></div></li>");
                $novo.children('li:last-child').toggle('slow');
            } else {
                $novo = $( this ).parent('.quadro-t').after("<ul><li class='children'><div class='quadro-t "+"'><i class='far fa-trash-alt action-button'></i><i class='fas fa-plus-circle action-button'></i><input type='text' class='input-text' value='New'/></div></div></li></ul>");
                $($novo).siblings('ul').toggle('slow');
            }
            $('.decision-icons').fadeOut(600,function() {$(this).css('display', 'none')});
        } else {
            if($( this ).parent().parent().parent().children('li').length > 1){
                $( this ).parent().parent().fadeOut(600,function() {
                    $( this ).remove();
                })
            } else {
                $( this ).parent().parent().parent().fadeOut(600,function() {
                    $( this ).remove();
                })
            }
        }
    });
    $('#tree').on("click", ".fa-plus-circle:not(.action-button)", function(event) {
        event.stopPropagation();
        $(this).siblings('.decision-icons').toggle("slow");
    })
})
