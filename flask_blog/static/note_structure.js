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
        var html = '<div style="font-size:' + (25-layer*5) + 'px">' + str + count + '. ' + this.title + '</div>';
        var newCount = 1;
        var newHead = str + count + '.';
        Array.prototype.forEach.call(this.children, child => {
            html += child.toHTML(newHead, newCount, layer+1);
            newCount += 1;
        });
        return html;
    }
}



var rootNode = new TreeNode('0', dict['0'].title);
rootNode.addChildren();

document.getElementById('note structure').innerHTML = rootNode.toHTML('', 1, 1);

