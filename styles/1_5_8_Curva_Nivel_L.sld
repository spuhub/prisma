<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0">
  <NamedLayer>
    <se:Name>ET_RDG Curva_Nivel</se:Name>
    <UserStyle>
      <se:Name>ET_RDG Curva_Nivel</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>Auxiliar</se:Name>
          <se:Description>
            <se:Title>Auxiliar</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipocurvanivel</ogc:PropertyName>
              <ogc:Literal>Auxiliar</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:MaxScaleDenominator>100000000</se:MaxScaleDenominator>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#602e00</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
              <se:SvgParameter name="stroke-dasharray">9 3</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Mestra</se:Name>
          <se:Description>
            <se:Title>Mestra</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipocurvanivel</ogc:PropertyName>
              <ogc:Literal>Mestra</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:MaxScaleDenominator>100000000</se:MaxScaleDenominator>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#602e00</se:SvgParameter>
              <se:SvgParameter name="stroke-width">2</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Normal</se:Name>
          <se:Description>
            <se:Title>Normal</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipocurvanivel</ogc:PropertyName>
              <ogc:Literal>Normal</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:MaxScaleDenominator>100000000</se:MaxScaleDenominator>
          <se:LineSymbolizer>
            <se:Stroke>
              <se:SvgParameter name="stroke">#602e00</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
              <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
            </se:Stroke>
          </se:LineSymbolizer>
        </se:Rule>
        <se:Rule>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipocurvanivel</ogc:PropertyName>
              <ogc:Literal>Mestra</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:MaxScaleDenominator>4001</se:MaxScaleDenominator>
          <se:TextSymbolizer>
            <se:Label>
              <ogc:PropertyName>cota</ogc:PropertyName>
            </se:Label>
            <se:Font>
              <se:SvgParameter name="font-family">MS Shell Dlg 2</se:SvgParameter>
              <se:SvgParameter name="font-size">10</se:SvgParameter>
            </se:Font>
            <se:LabelPlacement>
              <se:LinePlacement>
                <se:GeneralizeLine>true</se:GeneralizeLine>
              </se:LinePlacement>
            </se:LabelPlacement>
            <se:Halo>
              <se:Radius>1.5</se:Radius>
              <se:Fill>
                <se:SvgParameter name="fill">#ffffff</se:SvgParameter>
              </se:Fill>
            </se:Halo>
            <se:Fill>
              <se:SvgParameter name="fill">#724120</se:SvgParameter>
            </se:Fill>
          </se:TextSymbolizer>
        </se:Rule>
        <se:Rule>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>tipocurvanivel</ogc:PropertyName>
                <ogc:Literal>Normal</ogc:Literal>
              </ogc:PropertyIsEqualTo>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>tipocurvanivel</ogc:PropertyName>
                <ogc:Literal>Auxiliar</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <se:MaxScaleDenominator>2001</se:MaxScaleDenominator>
          <se:TextSymbolizer>
            <se:Label>
              <ogc:PropertyName>cota</ogc:PropertyName>
            </se:Label>
            <se:Font>
              <se:SvgParameter name="font-family">MS Shell Dlg 2</se:SvgParameter>
              <se:SvgParameter name="font-size">10</se:SvgParameter>
            </se:Font>
            <se:LabelPlacement>
              <se:LinePlacement>
                <se:GeneralizeLine>true</se:GeneralizeLine>
              </se:LinePlacement>
            </se:LabelPlacement>
            <se:Halo>
              <se:Radius>1.5</se:Radius>
              <se:Fill>
                <se:SvgParameter name="fill">#ffffff</se:SvgParameter>
              </se:Fill>
            </se:Halo>
            <se:Fill>
              <se:SvgParameter name="fill">#724120</se:SvgParameter>
            </se:Fill>
          </se:TextSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
