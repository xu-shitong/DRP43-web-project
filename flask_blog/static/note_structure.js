let note1 = JSON.parse(document.getElementById('canvas').getAttribute('note'));
let dict = note1.tree;

class TreeNode {

    constructor(id, title) {
        this.id = id;
        this.title = title;
        this.children = [];
    }

    addChildren() {
        var childrenIds = dict[this.id].child;
        Array.prototype.forEach.call(childrenIds, id => {
            var child = new TreeNode(id, dict[id].title);
            child.addChildren();
            this.children.push(child);
        })
    }

    toHTML(str, count, layer) {
        var newCount = 1;
        var newHead = str + count + '.';

        var html = '<div class="small " >';
        for (var i = 0; i < layer; i++) {
            html += '&nbsp;&nbsp;';
        }
        if (layer == 1) {
            html += '<strong>> ' + str + count + '- ' + this.title + '</strong>';
        } else {
            html += '> ' + str + count + '- ' + this.title;
        }
        
        Array.prototype.forEach.call(this.children, child => {
            html += child.toHTML(newHead, newCount, layer+1);
            newCount += 1;
        });
        html += '</div>'
        return html;
    }
}


var rootNode = new TreeNode('0', dict['0'].title);
rootNode.addChildren();

var html = '';
var count = 1;
Array.prototype.forEach.call(rootNode.children, child => {
    html += child.toHTML('',count, 1);
    count += 1;
})

document.getElementById('note structure').innerHTML = html;


