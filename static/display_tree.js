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
    } else {
        $newNode.addClass('no-children');
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
            createTree(data);
            $('#tree')
                .find('> .children > ul')
                .fadeOut(600,function() {$(this).css('display', 'block')});
        })
        .catch(error => {
            console.error('Erro on get tree:', error);
        });
});

function closeAll(){
    $('#tree ul').fadeOut(600,function() {$(this).css('display', 'none')});
}

function openAll(){
    $('#tree ul').fadeIn(600,function() {$(this).css('display', 'block')});
}

$(function(){
    $('#tree').on("click", ".quadro-t", function() {
        $( this ).siblings().toggle( "slow" );
    })
})
