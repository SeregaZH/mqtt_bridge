import pytest
from src.mqtt_bridge.enricher import create_enricher, Enricher
from sensor_msgs.msg import Temperature, NavSatFix


def test_create_enricher_should_create_enricher_if_config_specified(stub_enricher_config):
    # Act
    instance = create_enricher(('/test', Temperature), lambda result: result, stub_enricher_config)
    # Assert
    assert isinstance(instance, Enricher)

def test_create_enricher_should_return_none_if_config_not_specified():
    # Act
    instance = create_enricher(('/test', Temperature), lambda result: result)
    # Assert
    assert instance is None


@pytest.mark.parametrize('stub_messages, stub_result_message', [
    (
        [ NavSatFix(), Temperature() ], 
        { 'header': 
        { 'frame_id': '', 'seq': 0, 'stamp': {'nsecs': 0, 'secs': 0} }, 
        'latitude':0.0, 'longitude':0.0, 'temperature':0.0, 'variance':0.0}
    )
])
def test_enricher_should(mocker, stub_messages, stub_enricher_config, stub_result_message):

    # Arrange
    mocker.patch(
     'message_filters.ApproximateTimeSynchronizer.registerCallback',
      lambda self, callback: callback(*stub_messages)
     )
    stub_callback = mocker.stub() 
    
    # Act
    enricher = Enricher(('/test', Temperature), stub_callback, stub_enricher_config)

    # Assert
    assert isinstance(enricher, Enricher)
    stub_callback.assert_called_once_with(stub_result_message)
