import implicitFigures from 'markdown-it-image-figures'

export default ({ marp }) => marp.use(
    implicitFigures,
    { figcaption: "title" }
)
