"""
Convenience module intending to match the standard library ``json`` module.
"""

from typing import overload
from warnings import warn
from dataclasses import dataclass

from .. import core as syside


@dataclass
class SerializationError(Exception):
    """
    Error serializing element to SysML v2 JSON.
    """

    report: syside.SerdeReport[syside.Element]


@dataclass
class DeserializationError(Exception):
    """
    Error serializing element to SysML v2 JSON.
    """

    model: syside.DeserializedModel
    report: syside.SerdeReport[syside.Element | str | syside.DocumentSegment]


class SerdeWarning(Warning):
    """
    Class for warnings from serialization and deserialization
    """


def dumps(
    element: syside.Element,
    options: syside.SerializationOptions,
    indent: int = 2,
    use_spaces: bool = True,
    final_new_line: bool = True,
    include_cross_ref_uris: bool = True,
) -> str:
    """
    Serialize ``element`` to a SysML v2 JSON ``str``.

    See the documentation of the :py:class:`SerializationOptions
    <syside.SerializationOptions>` class for documentation of the possible
    options. The options object constructed with
    :py:meth:`SerializationOptions.minimal
    <syside.SerializationOptions.minimal>` instructs to produce a minimal JSON
    without any redundant elements that results in significantly smaller JSONs.
    Examples of redundant information that is avoided using minimal
    configuration are:

    +   including fields for null values;
    +   including fields whose values match the default values;
    +   including redefined fields that are duplicates of redefining fields;
    +   including derived fields that can be computed from minimal JSON (for
        example, the result value of evaluating an expression);
    +   including implied relationships.

    .. note::

        SysIDE does not construct all derived properties yet. Therefore, setting
        ``options.include_derived`` to ``True`` may result in a JSON that does
        not satisfy the schema.

    :param element:
        The SysML v2 element to be serialized to SysML v2 JSON.
    :param options:
        The serialization options to use when serializing SysML v2 to JSON.
    :param indent:
        How many space or tab characters to use for indenting the JSON.
    :param use_spaces:
        Whether use spaces or tabs for indentation.
    :param final_new_line:
        Whether to add a newline character at the end of the generated string.
    :param include_cross_ref_uris:
        Whether to add potentially relative URIs as ``@uri`` property to
        references of Elements from documents other than the one owning
        ``element``. Note that while such references are non-standard, they
        match the behaviour of XMI exports in Pilot implementation which use
        relative URIs for references instead of plain element IDs.
    :return:
        ``element`` serialized as JSON.
    """

    writer = syside.JsonStringWriter(
        indent=indent,
        use_spaces=use_spaces,
        final_new_line=final_new_line,
        include_cross_ref_uris=include_cross_ref_uris,
    )

    report = syside.serialize(element, writer, options)

    if not report:
        raise SerializationError(report)

    for msg in report.messages:
        if msg.severity == syside.DiagnosticSeverity.Warning:
            warn(msg.message, category=SerdeWarning, stacklevel=2)

    return writer.result


@overload
def loads(
    s: str,
    document: syside.Document,
    attributes: syside.AttributeMap | None = None,
) -> syside.DeserializedModel:
    """
    Deserialize a model from ``s`` into an already existing ``document``.

    :param s:
        The string contained serialized SysML model in JSON array.
    :param document:
        The document the model will be deserialized into.
    :param attributes:
        Attribute mapping of ``s``. If none provided, this will attempt to infer
        a corresponding mapping or raise a ``ValueError``.
    :return:
        Model deserialized from JSON array. Note that references into other
        documents will not be resolved, users will need to resolve them by
        calling ``link`` on the returned model. See also :py:class:`IdMap
        <syside.IdMap>`.
    """


@overload
def loads(
    s: str,
    document: syside.Url | str,
    attributes: syside.AttributeMap | None = None,
) -> tuple[syside.DeserializedModel, syside.SharedMutex[syside.Document]]:
    """
    Create a new ``document`` and deserialize a model from ``s`` into it.

    :param s:
        The string contained serialized SysML model in JSON array.
    :param document:
        A URI in the form of :py:class:`Url <syside.Url>` or a string, new
        document will be created with. If URI path has no extension, or the
        extension does not match ``sysml`` or ``kerml``, ``ValueError`` is
        raised.
    :param attributes:
        Attribute mapping of ``s``. If none provided, this will attempt to infer
        a corresponding mapping or raise a ``ValueError``.
    :return:
        Model deserialized from JSON array and the newly created document. Note that
        references into other documents will not be resolved, users will need to
        resolve them by calling ``link`` on the returned model. See also
        :py:class:`IdMap <syside.IdMap>`.
    """


def loads(
    s: str,
    document: syside.Document | syside.Url | str,
    attributes: syside.AttributeMap | None = None,
) -> (
    syside.DeserializedModel
    | tuple[syside.DeserializedModel, syside.SharedMutex[syside.Document]]
):
    """loads implementation"""
    reader = syside.JsonReader()

    new_doc: syside.SharedMutex[syside.Document] | None = None
    if isinstance(document, str):
        document = syside.Url(document)
    if isinstance(document, syside.Url):
        ext = document.path.rsplit(".", 1)[-1].lower()
        if ext == "sysml":
            lang = syside.ModelLanguage.SysML
        elif ext == "kerml":
            lang = syside.ModelLanguage.KerML
        else:
            raise ValueError(f"Unknown document language, could not infer from '{ext}'")
        new_doc = syside.Document.create_st(url=document, language=lang)
        with new_doc.lock() as doc:
            document = doc  # appease pylint

    with reader.bind(s) as json:
        if attributes is None:
            attributes = json.attribute_hint()
        if attributes is None:
            raise ValueError("Cannot deserialize model with unmapped attributes")

        model, report = syside.deserialize(document, json, attributes)

    if not report:
        raise DeserializationError(model, report)

    for msg in report.messages:
        if msg.severity == syside.DiagnosticSeverity.Warning:
            warn(msg.message, category=SerdeWarning, stacklevel=2)

    if new_doc:
        return model, new_doc
    return model
