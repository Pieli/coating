
# Program
input: text with tags
- hashmap with indicies  hashmap(index linenr : hasmap ( index positions:  string))
- view without tags
- onclick -> return tag



# TODO
- read from pipe
- read from file
- recognize tags




Find tag
if tag is empty -> take inner as label
if tag is not empty -> take label of tag
remember the line number of the tag
calculate the length of the inner tag
calculate the tag lengths (start and end)
calculate offsets



struct {
    tag_name        str
    inner_text      str
    y               int
    x               int
    x_raw           int
    len_tag_open    int (len(tag_name) + 2)
    len_tag_close   int  = 3
}
