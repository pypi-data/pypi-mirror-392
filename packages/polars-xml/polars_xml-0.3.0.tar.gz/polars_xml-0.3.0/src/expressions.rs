use polars::datatypes::DataType;
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

#[derive(Deserialize)]
struct XPathKwargs {
	xpath: String,
}

fn xpath_str_list<'a>(
	input: &'a str,
	xpath: &str,
) -> PolarsResult<Vec<String>> {
	let input = remove_namespaces(input)?;
	let package = sxd_document::parser::parse(&input)
		.map_err(|e| polars_err!(ComputeError: "{}", e))?;
	let document = package.as_document();
	let output = sxd_xpath::evaluate_xpath(&document, xpath)
		.map_err(|e| polars_err!(ComputeError: "{}", e))?;

	match output {
		sxd_xpath::Value::Nodeset(nodeset) => Ok(
			nodeset
				.into_iter()
				.map(|node| node.string_value())
				.collect(),
		),

		other => Ok(vec![format!("{}", other.into_string())]),
	}
}

fn list_dtype(input_fields: &[Field]) -> PolarsResult<Field> {
	let list_of_strings_dtype = DataType::List(Box::new(DataType::String));
	polars_plan::dsl::FieldsMapper::new(input_fields)
		.with_dtype(list_of_strings_dtype)
}

#[polars_expr(output_type_func=list_dtype)]
fn xpath(inputs: &[Series], kwargs: XPathKwargs) -> PolarsResult<Series> {
	let ca = inputs[0].str()?;
	let mut builder =
		ListStringChunkedBuilder::new(ca.name().clone(), ca.len(), 1);
	ca.iter().for_each(|value| {
		if let Some(value) = value {
			let result = xpath_str_list(value, &kwargs.xpath).ok();
			if let Some(result) = result {
				builder.append_values_iter(result.iter().map(|v| v.as_str()));
				return;
			}
		}
		builder.append_null();
	});
	Ok(builder.finish().into_series())
}

/// https://github.com/shepmaster/sxd-xpath/issues/142
fn remove_namespaces(xml: &str) -> PolarsResult<String> {
	let mut reader = quick_xml::Reader::from_str(xml);
	let mut writer = quick_xml::Writer::new(std::io::Cursor::new(Vec::new()));

	loop {
		match reader.read_event().unwrap() {
			quick_xml::events::Event::Eof => break,
			quick_xml::events::Event::Start(e)
				if e
					.try_get_attribute("xmlns")
					.map_err(|e| polars_err!(ComputeError: "{}", e))?
					.is_some() =>
			{
				let mut new_e = e.to_owned();
				new_e.clear_attributes();
				for attr in e.attributes() {
					let attr = attr.map_err(|e| polars_err!(ComputeError: "{}", e))?;
					if attr.key.0 == b"xmlns" {
						continue;
					}
					new_e.push_attribute(attr);
				}

				writer
					.write_event(quick_xml::events::Event::Start(new_e))
					.map_err(|e| polars_err!(ComputeError: "{}", e))?;
			}
			e => {
				writer.write_event(e)?;
			}
		}
	}

	String::from_utf8(writer.into_inner().into_inner())
		.map_err(|e| polars_err!(ComputeError: "{}", e))
}
