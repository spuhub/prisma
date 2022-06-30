<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0" xmlns:se="http://www.opengis.net/se" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <se:Name>ET_RDG Vegetacao</se:Name>
    <UserStyle>
      <se:Name>ET_RDG Vegetacao</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>Mangue</se:Name>
          <se:Description>
            <se:Title>Mangue</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>tipoveg</ogc:PropertyName>
              <ogc:Literal>Mangue</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#68907d</se:SvgParameter>
            </se:Fill>
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
                                          <ogc:PropertyIsEqualTo>
                                            <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                            <ogc:Literal>Desconhecido</ogc:Literal>
                                          </ogc:PropertyIsEqualTo>
                                          <ogc:PropertyIsEqualTo>
                                            <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                            <ogc:Literal>Caatinga</ogc:Literal>
                                          </ogc:PropertyIsEqualTo>
                                        </ogc:Or>
                                        <ogc:PropertyIsEqualTo>
                                          <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                          <ogc:Literal>Campinarana</ogc:Literal>
                                        </ogc:PropertyIsEqualTo>
                                      </ogc:Or>
                                      <ogc:PropertyIsEqualTo>
                                        <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                        <ogc:Literal>Cerrado</ogc:Literal>
                                      </ogc:PropertyIsEqualTo>
                                    </ogc:Or>
                                    <ogc:PropertyIsEqualTo>
                                      <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                      <ogc:Literal>Estepe</ogc:Literal>
                                    </ogc:PropertyIsEqualTo>
                                  </ogc:Or>
                                  <ogc:PropertyIsEqualTo>
                                    <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                    <ogc:Literal>Floresta</ogc:Literal>
                                  </ogc:PropertyIsEqualTo>
                                </ogc:Or>
                                <ogc:PropertyIsEqualTo>
                                  <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                  <ogc:Literal>Refúgio ecológico</ogc:Literal>
                                </ogc:PropertyIsEqualTo>
                              </ogc:Or>
                              <ogc:PropertyIsEqualTo>
                                <ogc:PropertyName>tipoveg</ogc:PropertyName>
                                <ogc:Literal>Brejo ou pântano</ogc:Literal>
                              </ogc:PropertyIsEqualTo>
                            </ogc:Or>
                            <ogc:PropertyIsEqualTo>
                              <ogc:PropertyName>tipoveg</ogc:PropertyName>
                              <ogc:Literal>Vegetação cultivada</ogc:Literal>
                            </ogc:PropertyIsEqualTo>
                          </ogc:Or>
                          <ogc:PropertyIsEqualTo>
                            <ogc:PropertyName>tipoveg</ogc:PropertyName>
                            <ogc:Literal>Vegetação de restinga</ogc:Literal>
                          </ogc:PropertyIsEqualTo>
                        </ogc:Or>
                        <ogc:PropertyIsEqualTo>
                          <ogc:PropertyName>tipoveg</ogc:PropertyName>
                          <ogc:Literal>Jardim</ogc:Literal>
                        </ogc:PropertyIsEqualTo>
                      </ogc:Or>
                      <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>tipoveg</ogc:PropertyName>
                        <ogc:Literal>Reflorestamento</ogc:Literal>
                      </ogc:PropertyIsEqualTo>
                    </ogc:Or>
                    <ogc:PropertyIsEqualTo>
                      <ogc:PropertyName>tipoveg</ogc:PropertyName>
                      <ogc:Literal>Vegetação de área de contato</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                  </ogc:Or>
                  <ogc:PropertyIsEqualTo>
                    <ogc:PropertyName>tipoveg</ogc:PropertyName>
                    <ogc:Literal>Vegetação secundária</ogc:Literal>
                  </ogc:PropertyIsEqualTo>
                </ogc:Or>
                <ogc:PropertyIsEqualTo>
                  <ogc:PropertyName>tipoveg</ogc:PropertyName>
                  <ogc:Literal>Campo</ogc:Literal>
                </ogc:PropertyIsEqualTo>
              </ogc:Or>
              <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>tipoveg</ogc:PropertyName>
                <ogc:Literal>Arvore isolada</ogc:Literal>
              </ogc:PropertyIsEqualTo>
            </ogc:Or>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#009e00</se:SvgParameter>
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
          <se:MaxScaleDenominator>2001</se:MaxScaleDenominator>
          <se:TextSymbolizer>
            <se:Label>
              <ogc:PropertyName>nome</ogc:PropertyName>
            </se:Label>
            <se:Font>
              <se:SvgParameter name="font-family">Arial</se:SvgParameter>
              <se:SvgParameter name="font-size">10</se:SvgParameter>
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
                <se:SvgParameter name="fill">#fdfdfd</se:SvgParameter>
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
