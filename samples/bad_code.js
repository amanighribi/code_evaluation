function processData(data, flag, mode, extra, another) {
    if (flag) {
        if (mode == 1) {
            if (extra != null) {
                if (extra > 0) {
                    console.log("very deeply nested, this is bad practice for readability and maintenance, and this line has been extended further to exceed the maximum line length threshold");   
                }
            }
        }
    }
    // TODO: handle the mode == 2 case properly, currently broken
    return data;
}