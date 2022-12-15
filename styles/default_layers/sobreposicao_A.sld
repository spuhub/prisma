<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0" xmlns:se="http://www.opengis.net/se" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <se:Name>ET_RDG Elemento_Fisiografico_Natural_a</se:Name>
    <UserStyle>
      <se:Name>ET_RDG Elemento_Fisiografico_Natural_a</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>Ilha</se:Name>
          <se:Description>
            <se:Title>Ilha</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
              <ogc:Literal>Ilha</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#d3a549</se:SvgParameter>
            </se:Fill>
            <se:Stroke>
              <se:SvgParameter name="stroke">#232323</se:SvgParameter>
              <se:SvgParameter name="stroke-opacity">0</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
            </se:Stroke>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Praia</se:Name>
          <se:Description>
            <se:Title>Praia</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
              <ogc:Literal>Praia</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#eaea96</se:SvgParameter>
            </se:Fill>
            <se:Stroke>
              <se:SvgParameter name="stroke">#232323</se:SvgParameter>
              <se:SvgParameter name="stroke-opacity">0</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
            </se:Stroke>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Outros</se:Name>
          <se:Description>
            <se:Title>Outros</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:Or>
              <ogc:Or>
                <ogc:Or>
                  <ogc:Or>
                    <ogc:Or>
                      <ogc:Or>
                        <ogc:Or>
                          <ogc:Or>
                            <ogc:Or>
                              <ogc:Or>
                                <ogc:Or>
                                  <ogc:Or>
                                    <ogc:Or>
                                      <ogc:Or>
                                        <ogc:Or>
                                          <ogc:Or>
                                            <ogc:Or>
                                              <ogc:Or>
                                                <ogc:Or>
                                                  <ogc:Or>
                                                    <ogc:PropertyIsEqualTo>
                                                      <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                                      <ogc:Literal>Banco de areia</ogc:Literal>
                                                    </ogc:PropertyIsEqualTo>
                                                    <ogc:PropertyIsEqualTo>
                                                      <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                                      <ogc:Literal>Cabo</ogc:Literal>
                                                    </ogc:PropertyIsEqualTo>
                                                  </ogc:Or>
                                                  <ogc:PropertyIsEqualTo>
                                                    <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                                    <ogc:Literal>Chapada</ogc:Literal>
                                                  </ogc:PropertyIsEqualTo>
                                                </ogc:Or>
                                                <ogc:PropertyIsEqualTo>
                                                  <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                                  <ogc:Literal>Dolina</ogc:Literal>
                                                </ogc:PropertyIsEqualTo>
                                              </ogc:Or>
                                              <ogc:PropertyIsEqualTo>
                                                <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                                <ogc:Literal>Duna</ogc:Literal>
                                              </ogc:PropertyIsEqualTo>
                                            </ogc:Or>
                                            <ogc:PropertyIsEqualTo>
                                              <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                              <ogc:Literal>Escarpa</ogc:Literal>
                                            </ogc:PropertyIsEqualTo>
                                          </ogc:Or>
                                          <ogc:PropertyIsEqualTo>
                                            <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                            <ogc:Literal>Falha</ogc:Literal>
                                          </ogc:PropertyIsEqualTo>
                                        </ogc:Or>
                                        <ogc:PropertyIsEqualTo>
                                          <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                          <ogc:Literal>Falésia</ogc:Literal>
                                        </ogc:PropertyIsEqualTo>
                                      </ogc:Or>
                                      <ogc:PropertyIsEqualTo>
                                        <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                        <ogc:Literal>Fenda</ogc:Literal>
                                      </ogc:PropertyIsEqualTo>
                                    </ogc:Or>
                                    <ogc:PropertyIsEqualTo>
                                      <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                      <ogc:Literal>Maciço</ogc:Literal>
                                    </ogc:PropertyIsEqualTo>
                                  </ogc:Or>
                                  <ogc:PropertyIsEqualTo>
                                    <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                    <ogc:Literal>Montanha</ogc:Literal>
                                  </ogc:PropertyIsEqualTo>
                                </ogc:Or>
                                <ogc:PropertyIsEqualTo>
                                  <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                  <ogc:Literal>Morro</ogc:Literal>
                                </ogc:PropertyIsEqualTo>
                              </ogc:Or>
                              <ogc:PropertyIsEqualTo>
                                <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                                <ogc:Literal>Península</ogc:Literal>
                              </ogc:PropertyIsEqualTo>
                            </ogc:Or>
                            <ogc:PropertyIsEqualTo>
                              <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                              <ogc:Literal>Pico</ogc:Literal>
                            </ogc:PropertyIsEqualTo>
                          </ogc:Or>
                          <ogc:PropertyIsEqualTo>
                            <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                            <ogc:Literal>Planalto</ogc:Literal>
                          </ogc:PropertyIsEqualTo>
                        </ogc:Or>
                        <ogc:PropertyIsEqualTo>
                          <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                          <ogc:Literal>Planície</ogc:Literal>
                        </ogc:PropertyIsEqualTo>
                      </ogc:Or>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                        <ogc:Literal>Ponta</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                    </ogc:Or>
                    <ogc:PropertyIsEqualTo>
                      <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                      <ogc:Literal>Rocha</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Or>
                  <ogc:PropertyIsEqualTo>
                    <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                    <ogc:Literal>Serra</ogc:Literal>
                  </ogc:PropertyIsEqualTo>
                </ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                  <ogc:Literal>Talude</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>tipoelemnat</ogc:PropertyName>
                <ogc:Literal>Outros</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#c3c342</se:SvgParameter>
            </se:Fill>
            <se:Stroke>
              <se:SvgParameter name="stroke">#232323</se:SvgParameter>
              <se:SvgParameter name="stroke-opacity">0</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
            </se:Stroke>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:MaxScaleDenominator>15000</se:MaxScaleDenominator>
          <se:TextSymbolizer>
            <se:Label>
              <ogc:PropertyName>nome</ogc:PropertyName>
            </se:Label>
            <se:Font>
              <se:SvgParameter name="font-family">Arial</se:SvgParameter>
              <se:SvgParameter name="font-size">13</se:SvgParameter>
            </se:Font>
            <se:LabelPlacement>
              <se:PointPlacement>
                <se:AnchorPoint>
                  <se:AnchorPointX>0</se:AnchorPointX>
                  <se:AnchorPointY>0.5</se:AnchorPointY>
                </se:AnchorPoint>
              </se:PointPlacement>
            </se:LabelPlacement>
            <se:Halo>
              <se:Radius>0.5</se:Radius>
              <se:Fill>
                <se:SvgParameter name="fill">#ffffff</se:SvgParameter>
              </se:Fill>
            </se:Halo>
            <se:Fill>
              <se:SvgParameter name="fill">#000000</se:SvgParameter>
            </se:Fill>
            <se:VendorOption name="maxDisplacement">1</se:VendorOption>
          </se:TextSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
