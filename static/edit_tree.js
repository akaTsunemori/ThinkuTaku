function createNode(key, value, parent, previousKeys = []) {
    const keyParts = key.split(', ');
    let formattedKey = keyParts[1].replace(/\bC\b/g, '') + ', ' + keyParts[2];

    const $newNode = $(`
        <li class="children">
            <div class="quadro-t">
                <span class="node-text">
                    ${formattedKey}
                </span>
            </div>
        </li>
    `);

    if (Object.keys(value).length > 0) {
        const $subTree = $('<ul style="display: none;"></ul>');
        $newNode.append($subTree);
        Object.entries(value).forEach(([childKey, childValue]) => {
            createNode(childKey, childValue, $subTree, [...previousKeys, key]);
        });
    }

    parent.append($newNode);
}

function createTree(data) {
    const $tree = $('#tree');
    const $root = $(`
        <li class="children">
            <div class="quadro-t pai">
            <span class="node-text">
                    Tree
                </span>
            </div>
        </li>
    `);
    const $subItems = $('<ul style="display: none;"></ul>');
    $tree.append($root);
    $root.append($subItems);

    Object.entries(data).forEach(([key, value]) => {
        createNode(key, value, $subItems);
    });
}


document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-tree')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            createTree(data);
        })
        .catch(error => {
            console.error('Erro on get tree:', error);
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
                $novo = $galho.append("<li class='children' style='display: none'><div class='quadro-t "+"'><i class='far fa-trash-alt action-button'></i><i class='fas fa-plus-circle action-button'></i><input type='text' class='input-text' value='Novo'/></div></div></li>");
                $novo.children('li:last-child').toggle('slow');
            } else {
                $novo = $( this ).parent('.quadro-t').after("<ul><li class='children'><div class='quadro-t "+"'><i class='far fa-trash-alt action-button'></i><i class='fas fa-plus-circle action-button'></i><input type='text' class='input-text' value='Novo'/></div></div></li></ul>");
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
